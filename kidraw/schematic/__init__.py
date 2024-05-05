
import math
from copy import deepcopy
from itertools import starmap


class Schematic:
    def __init__(self, name, refdes="U", description="", show_pin_text=True, show_refdes=True, show_name=True, power_symbol=False):
        self.description = description
        self.show_name = show_name
        self.name = Text(text=name, pos=None)
        self.show_refdes = show_refdes
        self.refdes = Text(text=refdes, pos=None)
        self.show_pin_text = show_pin_text
        self.power_symbol = power_symbol
        self.features = []

    @property
    def filename(self):
        return _clean_name(self.name.text)

    def doc(self):
        return f"""$CMP {_clean_name(self.name.text)}
D {self.description}
$ENDCMP"""

    def sch(self):
        sh = "Y" if self.show_pin_text else "N"
        pow = "P" if self.power_symbol else "N"
        show_refdes = "V" if self.show_refdes else "I"
        show_name = "V" if self.show_name else "I"
        features = "\n".join(str(x) for x in self.features)
        name_pos = self.name.pos
        refdes_pos = self.refdes.pos
        if name_pos is None:
            name_pos = (0, int(self.bounding_box[0][1] - 35))
        if refdes_pos is None:
            refdes_pos = (0, int(self.bounding_box[1][1] + 35))
        return """DEF {1} {0.refdes.text} 0 0 {2} {2} 1 F {3}
F0 "{0.refdes.text}" {7[0]} {7[1]} 50 H {4} {0.refdes.halign} {0.refdes.valign}NN
F1 "{1}" {8[0]} {8[1]} 50 H {5} {0.name.halign} {0.name.valign}NN
F2 "" 0 0 50 H I C CNN
F3 "" 0 0 50 H I C CNN
DRAW
{6}
ENDDRAW
ENDDEF""".format(self, _clean_name(self.name.text), sh, pow, show_refdes, show_name, features, name_pos, refdes_pos)

    @property
    def bounding_box(self):
        xmin, xmax, ymin, ymax = 0, 0, 0, 0
        for f in self.features:
            bb = f.bounding_box
            xmin = min(xmin, bb[0][0])
            ymin = min(ymin, bb[0][1])
            xmax = max(xmax, bb[1][0])
            ymax = max(ymax, bb[1][1])
        return (xmin, ymin), (xmax, ymax)


class _Struct:
    __attributes__ = {}

    def __init__(self, **kwargs):
        for k, v in self.__attributes__.items():
            setattr(self, k, deepcopy(v))
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __setattr__(self, k, v):
        if k not in self.__attributes__:
            raise ValueError(f"Not allowed to set {k} in this object")
        super(_Struct, self).__setattr__(k, v)


class Line(_Struct):
    __attributes__ = {
        "points": [],
        "width": 6,
        "filled": False,
    }

    def __str__(self):
        p = list(starmap("{0:.0f} {1:.0f}".format, self.points))
        f = "F" if self.filled else "N"
        return "P {0} 0 1 {1} {2} {3}".format(
            len(self.points), self.width, " ".join(p), f)

    @property
    def bounding_box(self):
        xmin, xmax, ymin, ymax = 0, 0, 0, 0
        for p in self.points:
            xmin = min(xmin, p[0])
            xmax = max(xmax, p[0])
            ymin = min(ymin, p[1])
            ymax = max(ymax, p[1])
        return (xmin, ymin), (xmax, ymax)


class Circle(_Struct):
    __attributes__ = {
        "center": (0, 0),
        "radius": 0,
        "width": 6,
        "filled": False,
    }

    def __str__(self):
        f = "F" if self.filled else "N"
        return f"C {self.center[0]} {self.center[1]} {self.radius} 0 1 {self.width} {f}"

    @property
    def bounding_box(self):
        return ((self.center[0] - self.radius,
                 self.center[1] - self.radius),
                (self.center[0] + self.radius,
                 self.center[1] + self.radius))


class Arc(_Struct):
    __attributes__ = {
        "center": (0, 0),
        "radius": 0,
        "angle_start": 0,
        "angle_end": 0,
        "width": 6,
        "filled": False,
    }

    def __str__(self):
        f = "F" if self.filled else "N"
        x, y = self.center
        a1, a2 = math.radians(self.angle_start), math.radians(self.angle_end)
        p1 = (x + math.cos(a1) * self.radius, y + math.sin(a1) * self.radius)
        p2 = (x + math.cos(a2) * self.radius, y + math.sin(a2) * self.radius)

        return f"A {self.center[0]} {self.center[1]} {self.radius} {self.angle_start * 10} {self.angle_end * 10} 0 1 {self.width} {f} {p1[0]} {p1[1]} {p2[0]} {p2[1]}"

    @property
    def bounding_box(self):
        return ((self.center[0] - self.radius,
                 self.center[1] - self.radius),
                (self.center[0] + self.radius,
                 self.center[1] + self.radius))


class Text(_Struct):
    Center = "C"
    Left = "L"
    Right = "R"
    Top = "U"
    Bottom = "D"

    __attributes__ = {
        "text": "",
        "pos": (0, 0),
        "font_size": 50,
        "halign": Center,
        "valign": Center,
    }

    def __str__(self):
        return f'T 0 {self.pos[0]} {self.pos[1]} {self.font_size} 0 0 1 "{self.text}" Normal 0 {self.halign} {self.valign}'

    @property
    def bounding_box(self):
        w = len(self.text) * self.font_size
        return ((self.pos[0] - w / 2,
                 self.pos[1] - self.font_size / 2),
                (self.pos[0] + w / 2,
                 self.pos[1] + self.font_size / 2))


class Pin(_Struct):
    Right = "R"
    Left = "L"
    Up = "U"
    Down = "D"

    Undefined = "U"
    Input = "I"
    Output = "O"
    Bidirectional = "B"
    Tristate = "T"
    Passive = "P"
    OpenCollector = "C"
    OpenEmitter = "E"
    NotConnected = "N"
    Power = "W"
    PowerFlag = "w"

    Plain = ""
    ActiveLow = "I"
    Clock = "C"
    Hidden = "N"

    __attributes__ = {
        "numbers": None,
        "name": "~",
        "pos": (0, 0),
        "len": 0,
        "font_size": 50,
        "dir": Right,
        "type": Undefined,
        "shape": Plain,
    }

    def __str__(self):
        if isinstance(self.numbers, int):
            self.numbers = [self.numbers]
        n, os = self.numbers[0], self.numbers[1:]
        ret = [
            f"X {self.name} {n} {self.pos[0]:.0f} {self.pos[1]:.0f} {self.len} {self.dir} {self.font_size} {self.font_size} 0 1 {self.type} {self.shape}",
        ]
        for o in os:
            ret.append(f"X {self.name} {o} {self.pos[0]:.0f} {self.pos[1]:.0f} 0 U 0 0 0 1 {self.type} N")
        return "\n".join(ret)

    @property
    def bounding_box(self):
        off = {
            Pin.Right: (self.len, 0),
            Pin.Left: (-self.len, 0),
            Pin.Up: (0, self.len),
            Pin.Down: (0, -self.len),
        }[self.dir]
        return self.pos, (self.pos[0] + off[0], self.pos[1] + off[1])


class ICBuilder:
    def __init__(self, schematic, num_pins, slot_spacing=150, pin_len=200, edge_margin=50, grid_snap=50, target_aspect_ratio=1.6):
        self._schematic = schematic
        self._num_pins = num_pins
        self._slot_spacing = slot_spacing
        self._pin_len = pin_len
        self._edge_margin = edge_margin
        self._grid_snap = grid_snap
        self._target_aspect_ratio = target_aspect_ratio

        self._side = None
        self._pins = {}
        self._slots_by_side = {
            Pin.Right: [],
            Pin.Left: [],
            Pin.Up: [],
            Pin.Down: [],
        }

    def __enter__(self):
        return self

    def __exit__(self, unused_exc_type, unused_exc_value, unused_traceback):
        slots_lr = max(len(self._slots_by_side[Pin.Left]),
                       len(self._slots_by_side[Pin.Right]))
        slots_ud = max(len(self._slots_by_side[Pin.Up]),
                       len(self._slots_by_side[Pin.Down]))
        slots_lr, slots_ud = self._correct_aspect_ratio(slots_lr, slots_ud)

        w = (max(slots_ud - 1, 0)) * self._slot_spacing + 2 * self._edge_margin
        h = (max(slots_lr - 1, 0)) * self._slot_spacing + 2 * self._edge_margin

        x1 = -w / 2
        if x1 % self._grid_snap != 0:
            x1 -= x1 % self._grid_snap
        y1 = h / 2
        if y1 % self._grid_snap != 0:
            y1 -= y1 % self._grid_snap

        # left pins
        x, y = x1 - self._pin_len, y1 - self._edge_margin
        for s in self._slots_by_side[Pin.Left]:
            if s is not None:
                s.len = self._pin_len
                s.pos = x, y
                s.dir = Pin.Right
                self._schematic.features.append(s)
            y -= self._slot_spacing

        # right pins
        x, y = x1 + w + self._pin_len, y1 - self._edge_margin
        for s in self._slots_by_side[Pin.Right]:
            if s is not None:
                s.len = self._pin_len
                s.pos = x, y
                s.dir = Pin.Left
                self._schematic.features.append(s)
            y -= self._slot_spacing

        # top pins
        x, y = x1 + self._edge_margin, y1 + self._pin_len
        for s in self._slots_by_side[Pin.Up]:
            if s is not None:
                s.len = self._pin_len
                s.pos = x, y
                s.dir = Pin.Down
                self._schematic.features.append(s)
            x += self._slot_spacing

        # bottom pins
        x, y = x1 + self._edge_margin, y1 - h - self._pin_len
        for s in self._slots_by_side[Pin.Down]:
            if s is not None:
                s.len = self._pin_len
                s.pos = x, y
                s.dir = Pin.Up
                self._schematic.features.append(s)
            x += self._slot_spacing

        # Chip outline
        self._schematic.features.append(
            Line(points=[
                (x1, y1),
                (x1 + w, y1),
                (x1 + w, y1 - h),
                (x1, y1 - h),
                (x1, y1),
            ]))

        # Hidden/don't care pins
        for n in range(1, self._num_pins + 1):
            if n in self._pins:
                continue
            self._schematic.features.append(
                Pin(numbers=n, pos=(x1 + n, y1 - 1), type=Pin.NotConnected, shape=Pin.Hidden))

    def _correct_aspect_ratio(self, slots_lr, slots_ud):
        if slots_ud > 0 and slots_lr > slots_ud:
            while slots_lr / slots_ud > self._target_aspect_ratio:
                slots_ud += 2
                self._slots_by_side[Pin.Up].insert(0, None)
                self._slots_by_side[Pin.Up].append(None)
                self._slots_by_side[Pin.Down].insert(0, None)
                self._slots_by_side[Pin.Down].append(None)
        elif slots_lr > 0 and slots_ud > slots_lr:
            while slots_ud / slots_lr > self._target_aspect_ratio:
                slots_lr += 2
                self._slots_by_side[Pin.Left].insert(0, None)
                self._slots_by_side[Pin.Left].append(None)
                self._slots_by_side[Pin.Right].insert(0, None)
                self._slots_by_side[Pin.Right].append(None)
        return slots_lr, slots_ud

    def side(self, side):
        self._side = side

    def pin(self, numbers, **kwargs):
        p = Pin(numbers=numbers, dir=self._side, **kwargs)
        if isinstance(numbers, int):
            numbers = [numbers]
        for n in numbers:
            if n <= 0 or n > self._num_pins:
                raise ValueError(f"Pin number must be from 1 to {self._num_pins}")
            if n in self._pins:
                raise ValueError("Duplicate definition of pin")  # TODO: better
            self._pins[n] = p
        self._slots_by_side[self._side].append(p)
        return p

    def gap(self, n):
        for _ in range(n):
            self._slots_by_side[self._side].append(None)


def _clean_name(n):
    return n.replace(" ", "_")
