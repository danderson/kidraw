import collections
import contextlib
import itertools
import math

from . import devices
from . import symbols

DefaultWidth = 6

class Align(object):
    Center = 'C'
    Left = 'L'
    Right = 'R'
    Top = 'T'
    Bottom = 'B'

class FillMode(object):
    Transparent = ''
    Foreground = 'F'
    Background = 'f'

class Orientation(object):
    Up = 'U'
    Down = 'D'
    Left = 'L'
    Right = 'R'

class Electrical(object):
    Input = 'I'
    Output = 'O'
    Bidirectional = 'B'
    Tristate = 'T'
    Passive = 'P'
    OpenCollector = 'C'
    OpenEmitter = 'E'
    NotConnected = 'N'
    Unspecified = 'U'
    PowerInput = 'W'
    PowerOutput = 'w'

class Shape(object):
    Regular = ''
    ActiveLow = 'I'
    Clock = 'C'

class Library(object):
    def __init__(self):
        self._devices = []
        self.std = devices.Devices(self)

    def _lib(self):
        return '\n'.join([
            'EESchema-LIBRARY Version 2.3',
            '#encoding utf-8',
        ] + [x._lib() for x in self._devices] + [
            '#End Library',
        ])

    def _doc(self):
        return '\n'.join([
            'EESchema-DOCLIB  Version 2.0',
            '#',
        ] + [x._doc() for x in self._devices] + [
            '#End Doc Library'
        ])

    def device(self, name, refdes, description='', show_name=True, show_pin_text=True, copy_from=None, pin_align=50, power=False, flip_labels=False):
        d = Device(name, refdes, description=description, show_name=show_name, show_pin_text=show_pin_text, pin_align=pin_align, power=power, flip_labels=flip_labels)
        if copy_from is not None:
            d._copyfrom(copy_from)
        self._devices.append(d)
        return d

class Transform(object):
    def __init__(self):
        self._xform = [[1, 0, 0],
                       [0, 1, 0],
                       [0, 0, 1]]

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
        
    def _fcoords(self, x, y):
        c = [x, y, 1]
        return self._vecmult(self._xform[0], c), self._vecmult(self._xform[1], c)

    def _coords(self, x, y):
        x, y = self._fcoords(x, y)
        return round(x), round(y)
        
    def translate(self, x, y):
        self._mult([[1, 0, x],
                    [0, 1, y],
                    [0, 0, 1]])

    def rotate(self, alpha):
        alpha = math.radians(alpha)
        self._mult([[math.cos(alpha), math.sin(alpha), 0],
                    [-math.sin(alpha), math.cos(alpha), 0],
                    [0, 0, 1]])

    def scale(self, sx, sy):
        self._mult([[sx, 0, 0],
                    [0, sy, 0],
                    [0, 0, 1]])

    @contextlib.contextmanager
    def save(self):
        saved = self._xform
        yield
        self._xform = saved

class Device(object):
    def __init__(self, name, refdes, description, show_name, show_pin_text, pin_align, power, flip_labels):
        self._name = name.replace(' ', '_')
        self._refdes = refdes
        self._description = description
        self._show_name = show_name
        self._show_pin_text = show_pin_text
        self._min_y, self._max_y = 0, 0
        self._assigned_pin_nums = set()
        self._parts = []
        self._pin_align = pin_align
        self._power = power
        self._flip_labels = flip_labels
        self.xform = Transform()
        self.symbols = symbols.Symbols(self)

    def _lib(self):
        kind = 'P' if self._power else 'N'
        show_pins = 'Y' if self._show_pin_text else 'N'
        show_name = 'V' if self._show_name else 'I'
        name_y = self._max_y+20 if self._flip_labels else self._min_y-20
        name_align = Align.Bottom if self._flip_labels else Align.Top
        show_refdes = 'I' if self._power else 'V'
        refdes_y = self._min_y-20 if self._flip_labels else self._max_y+20
        refdes_align = Align.Top if self._flip_labels else Align.Bottom
        return '\n'.join([
            'DEF %s %s 0 0 %s %s 1 F %s' % (self._name, self._refdes, show_pins, show_pins, kind),
            'F0 "%s" 0 %d 50 H %s C %sNN' % (self._refdes, refdes_y, show_refdes, refdes_align),
            'F1 "%s" 0 %d 50 H %s C %sNN' % (self._name, name_y, show_name, name_align),
            'F2 "" 0 0 50 H I C CNN',
            'F3 "" 0 0 50 H I C CNN',
            'DRAW',
        ] + [str(x) for x in self._parts] + [
            'ENDDRAW',
            'ENDDEF',
        ])

    def _doc(self):
        return '\n'.join([
            '$CMP %s' % self._name,
            'D %s' % self._description,
            '$ENDCMP',
        ])

    def _copyfrom(self, other):
        self.xform = Transform()
        self._min_y, self._max_y = other._min_y, other._max_y
        self._assigned_pin_nums = set(other._assigned_pin_nums)
        self._parts = list(other._parts)

    def line(self, *points, width=DefaultWidth, fillmode=FillMode.Transparent):
        points = [self.xform._coords(x, y) for x,y in points]
        p = ['%d %d' % (x, y) for x, y in points]
        self._min_y = min(self._min_y, min(x[1] for x in points))
        self._max_y = max(self._max_y, max(x[1] for x in points))
        self._parts.append(
            'P %d 0 1 %d %s %s' % (len(points), width, ' '.join(p), fillmode))

    def arc(self, a, b, c, width=DefaultWidth, fillmode=FillMode.Transparent):
        x1, y1 = self.xform._fcoords(*a)
        x2, y2 = self.xform._fcoords(*b)
        x3, y3 = self.xform._fcoords(*c)
        s1, s2, s3 = x1**2+y1**2, x2**2+y2**2, x3**2+y3**2

        self._min_y = min(self._min_y, y1, y2, y3)
        self._max_y = max(self._min_y, y1, y2, y3)

        # http://mathforum.org/library/drmath/view/55239.html
        cx = ((s1*y2 + s2*y3 + s3*y1 - s3*y2 - s2*y1 - s1*y3) /
              (x1*y2 + x2*y3 + x3*y1 - x3*y2 - x2*y1 - x1*y3) /
              2)
        cy = ((s2*x1 + s3*x2 + s1*x3 - s2*x3 - s1*x2 - s3*x1) /
              (x1*y2 + x2*y3 + x3*y1 - x3*y2 - x2*y1 - x1*y3) /
              2)
        r = math.sqrt((x1-cx)**2 + (y1-cy)**2)

        a1 = math.degrees(math.acos((x1-cx)/r))*10
        if y1-cy < 0:
            a1 *= -1
        a3 = math.degrees(math.acos((x3-cx)/r))*10
        if y3-cy < 0:
            a3 *= -1

        cx, cy, r, a1, a3, x1, y1, x3, y3 = round(cx), round(cy), round(r), round(a1), round(a3), round(x1), round(y1), round(x3), round(y3)

        self._parts.append(
            'A %d %d %d %d %d 0 1 %d %s %d %d %d %d' % (cx, cy, r, a1, a3, width, fillmode, x1, y1, x3, y3))
        
    def rectangle(self, topleft, bottomright, width=DefaultWidth, fillmode=FillMode.Transparent):
        (x1, y1), (x2, y2) = topleft, bottomright
        # Use a polyline instead of a rectangle, because rectangles can't be rotated.
        self.line((x1, y1), (x1, y2), (x2, y2), (x2, y1), (x1, y1), width=width, fillmode=fillmode)
        # self._parts.append(
        #     'S %d %d %d %d 0 1 %d %s' % (topleft[0], topleft[1], bottomright[0], bottomright[1], width, fillmode))
        
    def circle(self, x, y, radius, width=DefaultWidth, fillmode=FillMode.Transparent):
        x, y = self.xform._coords(x, y)
        self._min_y = min(self._min_y, y-radius)
        self._max_y = max(self._max_y, y+radius)
        self._parts.append(
            'C %d %d %d 0 1 %d %s' % (x, y, radius, width, fillmode))

    def text(self, x, y, text, angle=0.0, size=50, italic=False, bold=False, halign=Align.Center, valign=Align.Center):
        x, y = self.xform._coords(x, y)
        italic = 'Italic' if italic else 'Normal'
        bold = 1 if bold else 0
        self._parts.append(
            'T %d %d %d %d 0 0 1 "%s" %s %d %s %s' % (int(angle*10), x, y, size, text.replace('"', "'"), italic, bold, halign, valign))

    def pin(self, x1, y1, length=0, number=None, name='~', orientation=Orientation.Right, typ=Electrical.Passive, shape=Shape.Regular, visible=True):
        x2, y2 = x1, y1
        if orientation == Orientation.Up:
            y2 += length
        elif orientation == Orientation.Down:
            y2 -= length
        elif orientation == Orientation.Right:
            x2 += length
        elif orientation == Orientation.Left:
            x2 -= length

        x1, y1 = self.xform._coords(x1, y1)
        x2, y2 = self.xform._coords(x2, y2)
        dx, dy = x2 - x1, y2 - y1
        if dx != 0 and dy != 0:
            raise ValueError('Pin must be vertical or horizontal in final drawing')

        if dy > 0:
            orientation = Orientation.Up
        elif dy < 0:
            orientation = Orientation.Down
        elif dx > 0:
            orientation = Orientation.Right
        elif dx < 0:
            orientation = Orientation.Left

        self._min_y = min(self._min_y, y1, y2)
        self._max_y = max(self._max_y, y1, y2)
            
        if x1%self._pin_align != 0:
            raise ValueError('Pin X is not on the %dmil grid: %d' % (self._pin_align, x1))
        if y1%self._pin_align != 0:
            raise ValueError('Pin X is not on the %dmil grid: %d' % (self._pin_align, y1))
        if number is None:
            number = 1
            while number in self._assigned_pin_nums:
                number += 1
            self._assigned_pin_nums.add(number)
        if not visible:
            shape = 'N'+shape
        self._parts.append(
            'X %s %d %d %d %d %s 25 25 0 1 %s %s' % (name, number, x1, y1, length, orientation, typ, shape))

    @contextlib.contextmanager
    def build_ic(self, pin_grid=100, pin_length=150, edge_margin=50):
        b = ICBuilder(self, pin_grid, pin_length, edge_margin)
        yield b
        b._build()

class ICBuilder(object):
    def __init__(self, device, pin_grid, pin_length, edge_margin):
        self._d = device
        self._pin_grid = pin_grid
        self._pin_length = pin_length
        self._edge_margin = edge_margin
        self._pin_groups = collections.defaultdict(list) # Key: Orientation
        self._current_group = None

    def pin_group(self, orientation, gravity=Align.Center):
        self._current_group = []
        self._pin_groups[orientation].append(self._current_group)

    def pin(self, number, name, typ=Electrical.Passive, shape=Shape.Regular):
        self._current_group.append((number, name, typ, shape))

    def _draw_pins(self, groups, orientation):
        with self._d.xform.save():
            for g in groups:
                for number, name, typ, shape in g:
                    self._d.pin(0, 0, length=self._pin_length, orientation=orientation, number=number, name=name, typ=typ, shape=shape)
                    self._d.xform.translate(0, -self._pin_grid)
                self._d.xform.translate(0, -self._pin_grid)

    def _build(self):
        slots_left = sum(len(l) for l in self._pin_groups[Orientation.Left]) + max(0, len(self._pin_groups[Orientation.Left])-1)
        slots_right = sum(len(l)-1 for l in self._pin_groups[Orientation.Right]) + max(0, len(self._pin_groups[Orientation.Right])-1)
        slots_top = sum(len(l)-1 for l in self._pin_groups[Orientation.Up]) + max(0, len(self._pin_groups[Orientation.Up])-1)
        slots_bottom = sum(len(l)-1 for l in self._pin_groups[Orientation.Down]) + max(0, len(self._pin_groups[Orientation.Down])-1)

        slots_horiz = max(slots_left, slots_right, 2)-1
        slots_vert = max(slots_top, slots_bottom, 2)-1
        
        with self._d.xform.save():
            # Position at the top-left pin.
            self._d.xform.translate(-(slots_vert/2*self._pin_grid + self._edge_margin + self._pin_length),
                                    (slots_horiz/2*self._pin_grid))
            self._draw_pins(self._pin_groups[Orientation.Left], Orientation.Right)

            # Top right
            self._d.xform.translate(slots_vert*self._pin_grid + self._edge_margin*2 + self._pin_length*2, 0)
            self._draw_pins(self._pin_groups[Orientation.Right], Orientation.Left)
            # Rectangle top left
            self._d.xform.translate(-(slots_vert*self._pin_grid + self._edge_margin*2 + self._pin_length), self._edge_margin)
            self._d.rectangle((0, 0), (slots_vert*self._pin_grid + self._edge_margin*2, -(slots_horiz*self._pin_grid + self._edge_margin*2)))
                    

        # h = max(slots_left, slots_right, 2)*self._pin_grid/2 # mils
        # l = max(slots_top, slots_bottom, 2)*self._pin_grid/2 # mils
        # if h % self._edge_margin != 0:
        #     h += self._edge_margin - (h%self._edge_margin)
        # if l % self._edge_margin != 0:
        #     l += self._edge_margin - (l%self._edge_margin)

        # self._d.rectangle((-l, h), (l, -h))
        # y = h-self._edge_margin
        # for g in self._pin_groups[Orientation.Left]:
        #     for number, name, typ, shape in g:
        #         self._d.pin(-l-self._pin_length, y, length=self._pin_length, orientation=Orientation.Right, number=number, name=name, typ=typ, shape=shape)
        #         y -= self._pin_grid
        #     y -= self._pin_grid
        # y = h - self._edge_margin
        # for g in self._pin_groups[Orientation.Right]:
        #     for number, name, typ, shape in g:
        #         self._d.pin(l+self._pin_length, y, length=self._pin_length, orientation=Orientation.Left, number=number, name=name, typ=typ, shape=shape)
        #         y -= self._pin_grid
        #     y -= self._pin_grid

@contextlib.contextmanager
def library(pathprefix):
    l = Library()
    yield l
    with open(pathprefix+'.lib', 'w') as f:
        f.write(l._lib())
    with open(pathprefix+'.dcm', 'w') as f:
        f.write(l._doc())
