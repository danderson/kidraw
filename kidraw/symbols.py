import itertools

import kidraw

class _Lib(object):
    _sublibs = {}

    def __init__(self, device):
        self._d = device
        for n, cls in self._sublibs.items():
            setattr(self, n, cls(device))

class _Capacitor(_Lib):
    def __call__(self):
        self._d.line((-100, 0), (-10, 0))
        self._d.line((-10, -30), (-10, 30), width=10)
        self._d.line((10, -30), (10, 30), width=10)
        self._d.line((10, 0), (100, 0))

    def polarized(self):
        self()
        self._d.line((20, 20), (30, 20), width=3)
        self._d.line((25, 15), (25, 25), width=3)

class _Diode(_Lib):
    def __call__(self):
        self._d.line((-100, 0), (100, 0))
        self._d.line((-25, -25), (25, 0), (-25, 25), fillmode=kidraw.FillMode.Foreground)
        self._d.line((25, -25), (25, 25))

    def zener(self):
        self._d.line((-100, 0), (100, 0))
        self._d.line((-25, -25), (25, 0), (-25, 25), fillmode=kidraw.FillMode.Foreground)
        self._d.line((30, -25), (25, -20), (25, 20), (20, 25))

    def schottky(self):
        self()
        self._d.line((15, -15), (15, -25), (25, -25))
        self._d.line((25, 25), (35, 25), (35, 15))

class _Power(_Lib):
    def vcc(self):
        self._d.line((0, 0), (0, 50))
        self._d.line((-50, 50), (50, 50))

    def gnd(self):
        self._d.line((0, 0), (0, -50))
        self._d.line((-50, -50), (50, -50))
        self._d.line((-25, -75), (25, -75))
        self._d.line((-5, -100), (5, -100))

    def flag(self):
        self._d.line((0, 0), (0, 50), (50, 75), (0, 100), (-50, 75), (0, 50))
        self._d.text(0, 75, "PWR", size=15, bold=True)

class _Transistor(_Lib):
    class _BJT(_Lib):
        def _bjt(self):
            self._d.circle(0, 0, 70)
            self._d.line((-20, -50), (-20, 50), width=10)
            # Base
            self._d.line((-100, 0), (-20, 0))
            self._d.text(-90, -10, "B", size=20, halign=kidraw.Align.Right, valign=kidraw.Align.Top)
            # Collector/Emitter
            self._d.line((-20, 30), (50, 65))
            self._d.line((50, 65), (50, 100))
            self._d.text(60, 100, "C", size=20, halign=kidraw.Align.Left, valign=kidraw.Align.Top)
            self._d.line((-20, -30), (50, -65))
            self._d.line((50, -65), (50, -100))
            self._d.text(60, -100, "E", size=20, halign=kidraw.Align.Left, valign=kidraw.Align.Bottom)

        def npn(self):
            self._bjt()
            with self._d.xform.save():
                self._d.xform.translate(-20, -30)
                self._d.xform.rotate(26.56)
                self._d.line((60, 0), (30, 10), (30, -10), width=3, fillmode=kidraw.FillMode.Foreground)

        def pnp(self):
            self._bjt()
            with self._d.xform.save():
                self._d.xform.translate(-20, -30)
                self._d.xform.rotate(26.56)
                self._d.line((20, 0), (50, 10), (50, -10), width=3, fillmode=kidraw.FillMode.Foreground)

    class _JFET(_Lib):
        def _jfet(self):
            self._d.line((-25, -60), (-25, 60))
            self._d.line((-100, -50), (0, -50), (0, -100))
            self._d.line((-25, 50), (0, 50), (0, 100))
            self._d.circle(-20, 0, 70)
            self._d.text(-95, -60, "G", size=20, halign=kidraw.Align.Left, valign=kidraw.Align.Top)
            self._d.text(10, 100, "D", size=20, halign=kidraw.Align.Left, valign=kidraw.Align.Top)
            self._d.text(10, -100, "S", size=20, halign=kidraw.Align.Left, valign=kidraw.Align.Bottom)

        def n_channel(self):
            self._jfet()
            self._d.line((-25, -50), (-45, -60), (-45, -40), width=3, fillmode=kidraw.FillMode.Foreground)

        def p_channel(self):
            self._jfet()
            self._d.line((-55, -50), (-35, -60), (-35, -40), width=3, fillmode=kidraw.FillMode.Foreground)

    class _MOSFET(_Lib):
        def _mosfet(self):
            self._d.line((-100, -50), (-40, -50), (-40, 50))
            self._d.line((-30, -55), (-30, -31))
            self._d.line((-30, -12), (-30, 12))
            self._d.line((-30, 31), (-30, 55))

            self._d.line((-30, -43), (0, -43), (0, -100))
            self._d.line((-30, 43), (0, 43), (0, 100))
            self._d.line((-30, 0), (0, 0), (0, -43))

            self._d.circle(-15, 0, 70)
            self._d.text(-95, -60, "G", size=20, halign=kidraw.Align.Left, valign=kidraw.Align.Top)
            self._d.text(10, 100, "D", size=20, halign=kidraw.Align.Left, valign=kidraw.Align.Top)
            self._d.text(10, -100, "S", size=20, halign=kidraw.Align.Left, valign=kidraw.Align.Bottom)

        def n_channel(self):
            self._mosfet()
            self._d.line((-30, 0), (-10, 15), (-10, -15), width=2, fillmode=kidraw.FillMode.Foreground)

        def p_channel(self):
            self._mosfet()
            self._d.line((0, 0), (-20, 15), (-20, -15), width=2, fillmode=kidraw.FillMode.Foreground)

    _sublibs = {
        'bipolar': _BJT,
        'jfet': _JFET,
        'mosfet': _MOSFET,
    }

class Symbols(_Lib):
    _sublibs = {
        'capacitor': _Capacitor,
        'diode': _Diode,
        'power': _Power,
        'transistor': _Transistor,
    }

    def resistor(self):
        ys = itertools.cycle([0, 24, 0, -24])
        xs = range(-96, 96+1, 12)
        squiggle = [(-100, 0)] + list(zip(xs, ys)) + [(100, 0)]
        self._d.line(*squiggle)

    def inductor(self):
        def winding(x1, x2):
            r = abs(x2-x1)/2
            self._d.arc((x1, 0), (x1+r, r), (x2, 0))
        winding(-100, -50)
        winding(-50, 0)
        winding(0, 50)
        winding(50, 100)
    
    def led(self):
        self.diode()
        with self._d.xform.save():
            self._d.xform.translate(5, 35)
            self._d.xform.rotate(-60)
            for y in (-8, 8):
                self._d.line((-12, y), (12, y), width=3)
                self._d.line((12, y), (6, y+6), width=3)
                self._d.line((12, y), (6, y-6), width=3)
