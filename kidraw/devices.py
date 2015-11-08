import kidraw

class Devices(object):
    def __init__(self, library):
        self._l = library
        self.capacitor = _Capacitor(library)
        self.diode = _Diode(library)

    def resistor(self):
        d = self._l.device(name='Resistor', refdes='R', show_name=False, show_pin_text=False)
        with d.xform.save():
            d.xform.scale(0.8, 0.8)
            d.symbols.resistor()
        d.pin(-100, 0, length=20, orientation=kidraw.Orientation.Right)
        d.pin(100, 0, length=20, orientation=kidraw.Orientation.Left)

    def inductor(self):
        d = self._l.device(name='Inductor', refdes='L', show_name=False, show_pin_text=False)
        with d.xform.save():
            d.xform.scale(0.8, 0.8)
            d.symbols.inductor()
        d.pin(-100, 0, length=20, orientation=kidraw.Orientation.Right)
        d.pin(100, 0, length=20, orientation=kidraw.Orientation.Left)

    def led(self):
        d = self._l.device(name='LED', refdes='LED', show_name=False, show_pin_text=False)
        d.symbols.led()
        d.pin(-100, 0)
        d.pin(100, 0)

    # capacitor
    # capacitor.polarized
    # diode
    # diode.zener
    # diode.schottky

class _Capacitor(object):
    def __init__(self, library):
        self._l = library

    def __call__(self):
        d = self._l.device(name='Capacitor', refdes='C', show_name=False, show_pin_text=False)
        d.symbols.capacitor()
        d.pin(-100, 0)
        d.pin(100, 0)

    def polarized(self):
        d = self._l.device(name='Capacitor (Polarized)', refdes='C', show_name=False, show_pin_text=False)
        d.symbols.capacitor.polarized()
        d.pin(-100, 0)
        d.pin(100, 0)

class _Diode(object):
    def __init__(self, library):
        self._l = library

    def __call__(self):
        d = self._l.device(name='Diode', refdes='D', show_name=False, show_pin_text=False)
        d.symbols.diode()
        d.pin(-100, 0)
        d.pin(100, 0)

    def zener(self):
        d = self._l.device(name='Diode (Zener)', refdes='D', show_name=False, show_pin_text=False)
        d.symbols.diode.zener()
        d.pin(-100, 0)
        d.pin(100, 0)

    def schottky(self):
        d = self._l.device(name='Diode (Schottky)', refdes='D', show_name=False, show_pin_text=False)
        d.symbols.diode.schottky()
        d.pin(-100, 0)
        d.pin(100, 0)

