import kidraw

class _Lib(object):
    _sublibs = {}

    def __init__(self, library):
        self._l = library
        for n, cls in self._sublibs.items():
            setattr(self, n, cls(library))

class _Capacitor(_Lib):
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

class _Power(_Lib):
    def vcc(self, name='VCC'):
        d = self._l.device(name=name, refdes='#PWR', show_name=True, show_pin_text=False, power=True, flip_labels=True)
        d.symbols.power.vcc()
        d.pin(0, 0, name=name, typ=kidraw.Electrical.PowerInput, visible=False)

    def gnd(self, name='GND'):
        d = self._l.device(name=name, refdes='#PWR', show_name=True, show_pin_text=False, power=True)
        d.symbols.power.gnd()
        d.pin(0, 0, name=name, typ=kidraw.Electrical.PowerOutput, visible=False)

    def flag(self):
        d = self._l.device(name='PWR_FLAG', refdes='#FLG', show_name=False, show_pin_text=False, power=True)
        d.symbols.power.flag()
        d.pin(0, 0, typ=kidraw.Electrical.PowerInput, visible=False)

class _Transistor(_Lib):
    class _BJT(object):
        def __init__(self, library):
            self._l = library

        def npn(self, base_pin, collector_pin, emitter_pin, name='BJT (NPN)', show_name=False):
            d = self._l.device(name=name, refdes='Q', show_name=show_name, show_pin_text=False)
            d.symbols.transistor.bipolar.npn()
            d.pin(-100, 0, name='B', typ=kidraw.Electrical.Input, number=base_pin)
            d.pin(50, 100, name='C', number=collector_pin)
            d.pin(50, -100, name='E', number=emitter_pin)

        def pnp(self, base_pin, collector_pin, emitter_pin, name='BJT (PNP)', show_name=False):
            d = self._l.device(name=name, refdes='Q', show_name=show_name, show_pin_text=False)
            d.symbols.transistor.bipolar.pnp()
            d.pin(-100, 0, name='B', typ=kidraw.Electrical.Input, number=base_pin)
            d.pin(50, 100, name='C', number=collector_pin)
            d.pin(50, -100, name='E', number=emitter_pin)

    class _JFET(_Lib):
        def n_channel(self, gate_pin, drain_pin, source_pin, name='JFET (N-Channel)', show_name=False):
            d = self._l.device(name=name, refdes='Q', show_name=show_name, show_pin_text=False)
            d.symbols.transistor.jfet.n_channel()
            d.pin(-100, -50, name='G', typ=kidraw.Electrical.Input, number=gate_pin)
            d.pin(0, 100, name='D', number=drain_pin)
            d.pin(0, -100, name='S', number=source_pin)

        def p_channel(self, gate_pin, drain_pin, source_pin, name='JFET (P-Channel)', show_name=False):
            d = self._l.device(name=name, refdes='Q', show_name=show_name, show_pin_text=False)
            d.symbols.transistor.jfet.p_channel()
            d.pin(-100, -50, name='G', typ=kidraw.Electrical.Input, number=gate_pin)
            d.pin(0, 100, name='D', number=drain_pin)
            d.pin(0, -100, name='S', number=source_pin)

    class _MOSFET(_Lib):
        def n_channel(self, gate_pin, drain_pin, source_pin, name='MOSFET (N-Channel)', show_name=False):
            d = self._l.device(name=name, refdes='Q', show_name=show_name, show_pin_text=False)
            d.symbols.transistor.mosfet.n_channel()
            d.pin(-100, -50, name='G', typ=kidraw.Electrical.Input, number=gate_pin)
            d.pin(0, 100, name='D', number=drain_pin)
            d.pin(0, -100, name='S', number=source_pin)

        def p_channel(self, gate_pin, drain_pin, source_pin, name='MOSFET (P-Channel)', show_name=False):
            d = self._l.device(name=name, refdes='Q', show_name=show_name, show_pin_text=False)
            d.symbols.transistor.mosfet.p_channel()
            d.pin(-100, -50, name='G', typ=kidraw.Electrical.Input, number=gate_pin)
            d.pin(0, 100, name='D', number=drain_pin)
            d.pin(0, -100, name='S', number=source_pin)

    _sublibs = {
        'bipolar': _BJT,
        'jfet': _JFET,
        'mosfet': _MOSFET,
    }

    
class Devices(_Lib):
    _sublibs = {
        'capacitor': _Capacitor,
        'diode': _Diode,
        'power': _Power,
        'transistor': _Transistor,
    }

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
