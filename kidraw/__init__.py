from __future__ import with_statement
from __future__ import absolute_import
import contextlib
import enum
import math
import shutil
import os.path

RIGHT = 'R'
LEFT = 'L'
UP = 'U'
DOWN = 'D'

class Transform(object):
    def __init__(self):
        self._xform = [[1, 0, 0],
                       [0, 1, 0],
                       [0, 0, 1]]
        self._angle = 0.0
        self._saved = []
        self._x_minmax = (0, 0)
        self._y_minmax = (0, 0)

    def _vecmult(self, a, b):
        return sum(float(x)*float(y) for x,y in zip(a, b))
        
    def _mult(self, new):
        old = self._xform
        new = list(zip(*new))
        self._xform = [[0, 0, 0],
                       [0, 0, 0],
                       [0, 0, 0]]
        for row in range(3):
            for col in range(3):
                self._xform[row][col] = self._vecmult(old[row], new[col])

    def translate(self, x, y):
        """Move the origin by x horizontally and y vertically."""
        self._mult([[1, 0, x],
                    [0, 1, y],
                    [0, 0, 1]])

    def rotate(self, alpha):
        """Rotate clockwise by alpha degrees."""
        self._angle = ((self._angle + 180 + alpha) % 360) - 180
        alpha = math.radians(alpha)
        self._mult([[math.cos(alpha), math.sin(alpha), 0],
                    [-math.sin(alpha), math.cos(alpha), 0],
                    [0, 0, 1]])

    def scale(self, sx, sy):
        """Scale the grid by sx horizontally and sy vertically."""
        self._mult([[sx, 0, 0],
                    [0, sy, 0],
                    [0, 0, 1]])

    def push(self):
        self._saved.append((self._xform, self._angle))

    def pop(self):
        self._xform, self._angle = self._saved.pop()

    def fcoords(self, x, y):
        c = [x, y, 1]
        return self._vecmult(self._xform[0], c), self._vecmult(self._xform[1], c)

    def coords(self, x, y):
        x, y = self.fcoords(x, y)
        return round(x), round(y)

    def angle(self, alpha):
        return ((self._angle + 180 + alpha) % 360) - 180

    def boundingbox(self, x, y):
        x, y = self.coords(x, y)
        a, b = self._x_minmax
        self._x_minmax = (min(a, x), max(b, x))
        a, b = self._y_minmax
        self._y_minmax = (min(a, y), max(b, y))

    @property
    def x_min(self):
        return self._x_minmax[0]

    @property
    def x_max(self):
        return self._x_minmax[1]

    @property
    def y_min(self):
        return self._y_minmax[0]

    @property
    def y_max(self):
        return self._y_minmax[1]

class Library(object):
    def __init__(self):
        self._devices = {}

    def device(self, name):
        d = Device(name)

        if d.name in self._devices:
            raise RuntimeError('Tried to define device "%s" twice', name)
        self._devices[d.name] = d
        return d

    def _devs(self):
        return [d for _, d in sorted(self._devices.items())]

    def schematic_doc(self):
        return '''EESchema-DOCLIB  Version 2.0
#
%s
#End Doc Library''' % '\n'.join(d.doc() for d in self._devs())

    def schematic_lib(self):
        return '''EESchema-LIBRARY Version 2.3
#encoding utf-8
%s
#End Library''' % '\n'.join(d.sch() for d in self._devs())

    def footprint_lib(self):
        out = []
        for d in self._devs():
            for n, fp in d.footprints():
                out.append((n, fp))
        return out

    def write(self, filename_base):
        if os.path.isdir(filename_base):
            shutil.rmtree(filename_base)
        os.makedirs(filename_base)
        with open('%s/%s.lib' % (filename_base, filename_base), 'w') as f:
            f.write(self.schematic_lib())
        with open('%s/%s.dcm' % (filename_base, filename_base), 'w') as f:
            f.write(self.schematic_doc())
        for name, footprint in self.footprint_lib():
            with open('%s/%s.kicad_mod' % (filename_base, name), 'w') as f:
                f.write(footprint)

class Device(object):
    def __init__(self, name):
        self._name = name.replace(' ', '_')
        self._refdes = 'U'
        self._description = name
        self._show_pin_text = True
        self._show_name = True
        self._flip_text = False
        self._power_symbol = False
        self._num_pins = 0
        self._pins = {}
        self._schematic = Schematic(self._pins)
        self._footprints = {}

    @property
    def name(self):
        return self._name

    ## Mutators
    
    def refdes(self, refdes):
        self._refdes = refdes
        return self

    def description(self, description):
        self._description = description
        return self

    def hide_pin_text(self):
        self._show_pin_text = False
        return self

    def hide_name(self):
        self._show_name = False
        return self

    def flip_text(self):
        self._flip_text = True
        return self

    def power_symbol(self):
        self._power_symbol = True
        return self
    
    def num_pins(self, num_pins):
        if self._pins and max(self._pins.keys()) > num_pins:
            raise RuntimeError('Pin count is smaller than highest pin#')
        self._num_pins = num_pins

    def pin(self, *numbers):
        numbers = set(numbers)
        p = Pin(numbers)
        self._num_pins = max(self._num_pins, *numbers)
        for n in numbers:
            if n in self._pins:
                raise RuntimeError('Tried to define pin %d for %s twice', n, self._name)
            self._pins[n] = p
        return p
    
    def schematic(self):
        if self._schematic is not None:
            return self._schematic
        self._schematic = Schematic(self._pins)
        return self._schematic

    def footprint(self, name):
        f = Footprint(name, self._pins)
        if f.name in self._footprints:
            raise RuntimeError('Tried to define footprint "%s" twice', name)
        self._footprints[f.name] = f
        return f

    ## Outputters

    def doc(self):
        return '''$CMP %s
D %s
$ENDCMP''' % (self._name, self._description)

    def sch(self):
        (_, ymin), (_, ymax) = self._schematic.boundingbox()
        ytop, ybot = ymax+20, ymin-20
        return '''DEF %(name)s %(refdes)s 0 0 %(show_pins)s %(show_pins)s 1 F %(kind)s
F0 "%(refdes)s" 0 %(refdes_y)d 50 H %(refdes_show)s C %(refdes_align)sNN
F1 "%(name)s" 0 %(name_y)d 50 H %(name_show)s C %(name_align)sNN
F2 "" 0 0 50 H I C CNN
F3 "" 0 0 50 H I C CNN
DRAW
%(drawing)s
ENDDRAW
ENDDEF''' % {
    'name': self._name,
    'refdes': self._refdes,
    'show_pins': 'Y' if self._show_pin_text else 'N',
    'kind': 'P' if self._power_symbol else 'N',
    'power_hash': '#' if self._power_symbol else '',
    'refdes_y': ybot if self._flip_text else ytop,
    'refdes_show': 'I' if self._power_symbol else 'V',
    'refdes_align': 'T' if self._flip_text else 'B',
    'name_y': ytop if self._flip_text else ybot,
    'name_show': 'V' if self._show_name else 'I',
    'name_align': 'B' if self._flip_text else 'T',
    'drawing': self._schematic.sch(),
}

    def footprints(self):
        return dict(('%s_%s' % (self.name, f.name), f.footprint()) for f in self._footprints)

class Pin(object):
    def __init__(self, numbers=[]):
        self._numbers = set(numbers)
        self._name = str(min(numbers))
        self._type = 'U'

    @property
    def numbers(self):
        return self._numbers
        
    def _set_type(self, t):
        if self._type != 'U':
            raise RuntimeError('Tried to set pin type twice')
        self._type = t
        return self

    def name(self, n):
        self._name = n.replace(' ', '_')
        return self

    ##
    ## Electrical type
    ##
        
    def input(self):
        return self._set_type('I')

    def output(self):
        return self._set_type('O')

    def bidirectional(self):
        return self._set_type('B')

    def tristate(self):
        return self._set_type('T')

    def passive(self):
        return self._set_type('P')

    def open_collector(self):
        return self._set_type('C')

    def open_emitter(self):
        return self._set_type('E')

    def not_connected(self):
        return self._set_type('N')

    def power(self):
        return self._set_type('W')

    def power_flag(self):
        return self._set_type('w')

class Schematic(object):
    def __init__(self, pins):
        self._pin_ref = pins
        self._commands = []

    ###

    def translate(self, x, y):
        def run(out, xform):
            xform.translate(x, y)
        self._commands.append(run)
        return self

    def rotate(self, a):
        def run(out, xform):
            xform.rotate(a)
        self._commands.append(run)
        return self

    def scale(self, sx, sy):
        def run(out, xform):
            xform.scale(sx, sy)
        self._commands.append(run)
        return self

    @contextlib.contextmanager
    def save_position(self):
        self._commands.append(lambda _, xform: xform.push())
        yield
        self._commands.append(lambda _, xform: xform.pop())

    ###

    def clear(self):
        self._commands = []
    
    class _Line(object):
        def __init__(self, points):
            self._points = points
            self._width = 6
            self._filled = False

        def width(self, w):
            self._width = w
            return self

        def filled(self):
            self._filled = True
            return self

        def __call__(self, out, xform):
            for x, y in self._points:
                xform.boundingbox(x, y)
            p = ['%d %d' % xform.coords(x, y) for x, y in self._points]
            out.append('P %d 0 1 %d %s %s' % (len(p), self._width, ' '.join(p), 'F' if self._filled else 'N'))

    def line(self, *points):
        self._commands.append(self._Line(points))
        return self._commands[-1]

    def rect(self, p1, p2):
        (x1, y1), (x2, y2) = p1, p2
        return self.line((x1, y1), (x1, y2), (x2, y2), (x2, y1), (x1, y1))

    class _Circle(object):
        def __init__(self, pos, r):
            self._pos = pos
            self._radius = r
            self._width = 6
            self._filled = False

        def width(self, w):
            self._width = w
            return self

        def filled(self):
            self._filled = True
            return self

        def __call__(self, out, xform):
            x, y = self._pos
            xform.boundingbox(x-self._radius, y-self._radius)
            xform.boundingbox(x+self._radius, y+self._radius)
            a, b = xform.coords(x, y)
            out.append('C %d %d %d 0 1 %d %s' % (a, b, self._radius, self._width, 'F' if self._filled else 'N'))
    
    def circle(self, center, radius):
        self._commands.append(self._Circle(center, radius))
        return self._commands[-1]

    class _Pin(object):
        def __init__(self, number, pin_ref):
            self._number = number
            self._pin_ref = pin_ref
            self._pos = (0, 0)
            self._len = 0
            self._font_size = 50
            self._dir = RIGHT
            self._shape = ''

        def pos(self, x, y):
            self._pos = (x, y)
            return self

        def len(self, l):
            self._len = l
            return self

        def font_size(self, s):
            self._font_size = s
            return self
        
        def dir(self, d):
            self._dir = d
            return self

        def active_low(self):
            self._shape = 'I'
            return self

        def clock(self):
            self._shape = 'C'
            return self

        def hidden(self):
            self._shape = 'N'
            return self
        
        def __call__(self, out, xform):
            x, y = self._pos
            xform.boundingbox(x, y)
            if self._dir == RIGHT:
                xform.boundingbox(x+self._len, y)
            elif self._dir == LEFT:
                xform.boundingbox(x-self._len, y)
            elif self._dir == UP:
                xform.boundingbox(x, y+self._len)
            elif self._dir == DOWN:
                xform.boundingbox(x, y-self._len)
            x, y = xform.coords(x, y)
            out.append('X %s %d %d %d %d %s %d %d 0 1 %s %s' % (self._pin_ref._name, self._number, x, y, self._len, self._dir, self._font_size, self._font_size, self._pin_ref._type, self._shape))
            for n in self._pin_ref.numbers:
                if n == self._number:
                    continue
                out.append('X ~ %d %d %d 0 U 0 0 0 1 %s N' % (n, x, y, self._pin_ref._type))

    def pin(self, *numbers):
        numbers = set(numbers)
        pins = set([frozenset(getattr(self._pin_ref.get(x), 'numbers', set())) for x in numbers])
        if len(pins) != 1:
            raise RuntimeError('Drawing nonsensical pin')
        if list(pins)[0] != numbers:
            raise RuntimeError('Pin numbers must match between device and schematic')
        n = sorted(numbers)[0]
        p = self._Pin(n, self._pin_ref[n])
        self._commands.append(p)
        return p

    class _Arc(object):
        def __init__(self, pos, radius, a1, a2):
            self._pos = pos
            self._radius = radius
            self._angles = (a1, a2)
            self._width = 6
            self._filled = False

        def width(self, w):
            self._width = w
            return self

        def filled(self):
            self._filled = True
            return self

        def __call__(self, out, xform):
            x, y = self._pos
            a1, a2 = self._angles
            xform.boundingbox(x-self._radius, y-self._radius)
            xform.boundingbox(x+self._radius, y+self._radius)
            a, b = xform.coords(x, y)
            x1, y1 = xform.coords(x+(math.cos(math.radians(a1))*self._radius), y+(math.sin(math.radians(a1))*self._radius))
            x2, y2 = xform.coords(x+(math.cos(math.radians(a2))*self._radius), y+(math.sin(math.radians(a2))*self._radius))
            
            out.append('A %d %d %d %d %d 0 1 %d %s %d %d %d %d' % (a, b, self._radius, xform.angle(a1)*10, xform.angle(a2)*10, self._width, 'F' if self._filled else 'N', x1, y1, x2, y2))

    def arc(self, center, radius, a1, a2):
        self._commands.append(self._Arc(center, radius, a1, a2))
        return self._commands[-1]

    class _Text(object):
        def __init__(self, pos, txt):
            self._txt = txt
            self._pos = pos
            self._font_size = 50
            self._halign = 'C'
            self._valign = 'C'

        def font_size(self, sz):
            self._font_size = sz
            return self

        def halign(self, align):
            self._halign = align
            return self
        
        def valign(self, align):
            self._valign = align
            return self

        def __call__(self, out, xform):
            a, b = xform.coords(*self._pos)
            out.append('T 0 %d %d %d 0 0 1 "%s" Normal 0 %s %s' % (a, b, self._font_size, self._txt, self._halign, self._valign))

    def text(self, pos, txt):
        self._commands.append(self._Text(pos, txt))
        return self._commands[-1]

    def sch(self):
        out, xform = [], Transform()
        for cmd in self._commands:
            cmd(out, xform)
        return '\n'.join(out)

    def boundingbox(self):
        out, xform = [], Transform()
        for cmd in self._commands:
            cmd(out, xform)
        return (xform.x_min, xform.y_min), (xform.x_max, xform.y_max)

class Footprint(object):

    class _Feature(object):
        def __init__(self):
            self._side = 'F'
            self._layer = 'SilkS'
            self._width = 0.15

        def top(self):
            self._side = 'F'
            return self

        def bottom(self):
            self._side = 'B'
            return self

        def silkscreen(self):
            self._layer = 'SilkS'
            return self
            
        def fab(self):
            self._layer = 'Fab'
            return self

        def width(self, w):
            self._width = w
        
    def __init__(self, name, pins):
        self._name = name.replace(' ', '_')
        self._pin_ref = pins
        self._mask_margin = None
        self._paste_margin = None
        self._clearance = None
        self._commands = []

    @property
    def name(self):
        return self._name
        
    def mask_margin(self, m):
        self._mask_margin = m
        return self

    def paste_margin(self, m):
        self._paste_margin = -m
        return self

    def clearance(self, m):
        self._clearance = m
        return self

    def _cmd(self, f):
        self._commands.append(f)
        return self._commands[-1]
        
    class _Pad(object):
        def __init__(self, number):
            self._number = number
            self._pos = (0, 0)
            self._shape = 'circle'
            self._size = (0, 0)
            self._type = None
            self._drill = None
            self._mask_margin = None
            self._paste_margin = None
            self._clearance = None
            self._thermal_width = None
            self._thermal_gap = None

        def pos(self, x, y):
            self._pos = (x, y)
            return self

        ## Pad type
        
        def smd(self):
            self._type = 'smd'
            self._drill = None
            return self

        def thruhole(self, drill_diameter):
            self._type = 'thru_hole'
            self._drill = drill_diameter
            return self

        def test_point(self):
            self._type = 'connector'
            self._drill = None
            return self
        connector = test_point
            
        ## Pad shape
        
        def rect(self, w, h):
            self._size = (w, h)
            return self

        def circle(self, r):
            self._size = (r, r)
            return self

        def oval(self, w, h):
            self._size = (w, h)
            return self

        ## Misc

        def drill(self, size):
            self._drill = size
            return self

        def mask_margin(self, m):
            self._mask_margin = m
            return self

        def paste_margin(self, m):
            self._paste_margin = -m
            return self

        def clearance(self, m):
            self._clearance = m
            return self
        
        def thermal_relief(self, width, gap):
            self._thermal_width = width
            self._thermal_gap = gap
            return self

        def __call__(self, out, xform):
            shape = self._shape or ('rect' if self._smd else 'circle')
            out.append('(pad %s %s %s' % (self._number, self._type, shape))
            out.append('(at %d %d)' % xform.coords(*self._pos))
            out.append('(size %d %d)' % self._size)
            if self._type == 'smd' or self._type == 'connector':
                out.append('(layers F.Cu F.Paste F.Mask F.SilkS)')
            else:
                out.append('(layers *.Cu *.Mask F.SilkS)')
                out.append('(drill %d)' % self._drill)
            if self._mask_margin is not None:
                out.append('(solder_mask_margin %d)' % self._mask_margin)
            if self._paste_margin is not None:
                out.append('(solder_paste_margin %d)' % self._paste_margin)
            if self._clearance is not None:
                out.append('(clearance %d)' % self._clearance)
            if self._thermal_width is not None:
                out.append('(zone_connect 1)')
                out.append('(thermal_width %d)' % self._thermal_width)
                out.append('(thermal_gap %d)' % self._thermal_gap)
            out.append(')')

    def pad(self, number):
        if number not in self._pin_ref:
            raise RuntimeError('Cannot draw non-existent pin')
        return self._cmd(self._Pad(number))

    class _Text(_Feature):
        def __init__(self, typ, txt):
            super(_Text, self).__init__()
            self._typ = typ
            self._text = txt
            self._pos = (0, 0)
            self._size = None
            self._thickness = None

        def pos(self, x, y):
            self._pos = (x, y)
            return self

        def size(self, x, y):
            self._size = (x, y)
            return self

        def thickness(self, t):
            self._thickness = t
            return self

        def __call__(self, out, xform):
            out.append('(fp_text %s "%s"' % (self._typ, self._text))
            out.append('(at %d %d)' % xform.coords(*self._pos))
            out.append('(layer F.SilkS)')
            if self._size is not None or self._thickness is not None:
                out.append('(effects (font ')
                if self._size is not None:
                    out.append('(size %d %d)' % self._size)
                if self._thickness is not None:
                    out.append('(thickness %d)' % self._thickness)
                out.append(') )')
            out.append(')')
            
    def text(self, txt):
        return self._cmd(self._Text('user', txt))

    def refdes(self):
        return self._cmd(self._Text('reference', 'REFDES'))

    def value(self):
        return self._cmd(self._Text('value', 'VALUE'))

    class _Line(_Feature):
        def __init__(self, start, end):
            super(_Line, self).__init__()
            self._start = start
            self._end = end

        def __call__(self, out, xform):
            out.append('(fp_line (layer F.SilkS)')
            out.append('(start %d %d)' % xform.coords(*self._start))
            out.append('(end %d %d)' % xform.coords(*self._end))
            out.append('(width %d)' % self._width)
            out.append(')')

    def line(self, start, end):
        return self._cmd(self._Line(start, end))

    class _Circle(_Feature):
        def __init__(self, center, radius):
            super(_Circle, self).__init__()
            self._center = center
            self._radius = radius
            
        def __call__(self, out, xform):
            out.append('(fp_circle (layer F.SilkS)')
            out.append('(center %d %d)' % xform.coords(*self._center))
            out.append('(end %d %d)' % xform.coords(self._center[0]+self._radius, self._center[1]))
            out.append('(width %d)' % self._width)
            out.append(')')

    def circle(self, center, r):
        return self._cmd(self._Circle(center, r))

    def arc(self):
        raise NotImplementedError

    def poly(self):
        raise NotImplementedError

    def footprint(self):
        out, xform = [], Transform()
        if self._mask_margin is not None:
            out.append('(solder_mask_margin %d)' % self._mask_margin)
        if self._paste_margin is not None:
            out.append('(solder_paste_margin %d)' % self._paste_margin)
        if self._clearance is not None:
            out.append('(clearance %d)' % self._clearance)
        for cmd in self._commands:
            cmd(out, xform)
        draw = ' '.join(out)
        return '(module %s (layer F.Cu) (tedit 0) %s )' % (self.name, draw)
