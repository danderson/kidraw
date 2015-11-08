import itertools

import kidraw

class Symbols(object):
    def __init__(self, device):
        self._d = device
        self.capacitor = _Capacitor(device)
        self.diode = _Diode(device)

    def resistor(self):
        ys = itertools.cycle([0, 24, 0, -24])
        xs = range(-96, 96+1, 12)
        squiggle = [(-100, 0)] + list(zip(xs, ys)) + [(100, 0)]
        self._d.line(*squiggle)

    # capacitor
    # capacitor.polarized
    # diode
    # diode.zener
    # diode.schottky

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

class _Capacitor(object):
    def __init__(self, device):
        self._d = device

    def __call__(self):
        self._d.line((-100, 0), (-10, 0))
        self._d.line((-10, -30), (-10, 30), width=10)
        self._d.line((10, -30), (10, 30), width=10)
        self._d.line((10, 0), (100, 0))

    def polarized(self):
        self()
        self._d.line((20, 20), (30, 20), width=3)
        self._d.line((25, 15), (25, 25), width=3)

class _Diode(object):
    def __init__(self, device):
        self._d = device

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
