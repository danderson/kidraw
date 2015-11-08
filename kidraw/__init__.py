import contextlib
import itertools
import math

from . import devices
from . import symbols

DefaultWidth = 6

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

    def device(self, name, refdes, description='', show_name=True, show_pin_text=True, copy_from=None, pin_align=50):
        d = Device(name, refdes, description=description, show_name=show_name, show_pin_text=show_pin_text, pin_align=pin_align)
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
    def __init__(self, name, refdes, description='', show_name=True, show_pin_text=True, pin_align=50):
        self._name = name.replace(' ', '_')
        self._refdes = refdes
        self._description = description
        self._show_name = show_name
        self._show_pin_text = show_pin_text
        self._min_y, self._max_y = 0, 0
        self._assigned_pin_nums = set()
        self._parts = []
        self._pin_align = pin_align
        self.xform = Transform()
        self.symbols = symbols.Symbols(self)

    def _lib(self):
        show_pins = 'Y' if self._show_pin_text else 'N'
        show_name = 'V' if self._show_name else 'I'
        return '\n'.join([
            'DEF %s %s 0 0 %s %s 1 F N' % (self._name, self._refdes, show_pins, show_pins),
            'F0 "%s" 0 %d 50 H V C BNN' % (self._refdes, self._max_y+20),
            'F1 "%s" 0 %d 50 H %s C TNN' % (self._name, self._min_y-20, show_name),
            'F2 "" 0 0 50 H I C CNN',
            'F3 "" 0 0 50 H I C CNN',
            'DRAW',
        ] + [str(x) for x in self._parts] + [
            'ENDDRAW',
            'ENDDEF',
        ])

    def _doc(self):
        return '\n'.join([
            '$CMP C',
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
        topleft, bottomright = self.xform._coords(*topleft), self.xform._coords(*bottomright)
        self._min_y = min(self._min_y, topleft[1], bottomright[1])
        self._max_y = max(self._max_y, topleft[1], bottomright[1])
        self._parts.append(
            'S %d %d %d %d 0 1 %d %s' % (topleft[0], topleft[1], bottomright[0], bottomright[1], width, fillmode))
        
    def circle(self, center, radius, width=DefaultWidth, fillmode=FillMode.Transparent):
        x, y = self.xform._coords(*center)
        self._min_y = min(self._min_y, y-radius)
        self._max_y = max(self._max_y, y+radius)
        self._parts.append(
            'C %d %d %d 0 1 %d %s' % (x, y, radius, width, fillmode))

    def pin(self, x, y, length=0, number=None, name='~', orientation=Orientation.Right, typ=Electrical.Passive, shape=Shape.Regular):
        if length > 0:
            if orientation == Orientation.Up:
                self.line((x, y), (x, y+length))
            elif orientation == Orientation.Down:
                self.line((x, y), (x, y-length))
            elif orientation == Orientation.Right:
                self.line((x, y), (x+length, y))
            elif orientation == Orientation.Left:
                self.line((x, y), (x-length, y))

        x, y = self.xform._coords(x, y)
        if x%self._pin_align != 0:
            raise ValueError('Pin X is not on the %dmil grid: %d' % (self._pin_align, x))
        if y%self._pin_align != 0:
            raise ValueError('Pin X is not on the %dmil grid: %d' % (self._pin_align, y))
        if number is None:
            number = 1
            while number in self._assigned_pin_nums:
                number += 1
            self._assigned_pin_nums.add(number)
        self._parts.append(
            'X %s %d %d %d 0 %s 50 50 0 1 %s %s' % (name, number, x, y, orientation, typ, shape))

@contextlib.contextmanager
def library(pathprefix):
    l = Library()
    yield l
    with open(pathprefix+'.lib', 'w') as f:
        f.write(l._lib())
    with open(pathprefix+'.dcm', 'w') as f:
        f.write(l._doc())
