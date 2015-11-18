from __future__ import with_statement
from __future__ import absolute_import
import kidraw

def vcc(l, name='VCC'):
    d = l.device(name).refdes('#PWR').power_symbol().hide_pin_text().flip_text()
    d.pin(1).name(name).power()
    s = d.schematic()
    s.pin(1).hidden()
    s.line((0, 0), (0, 50))
    s.line((-50, 50), (50, 50))
    return d

def gnd(l, name='GND'):
    d = l.device(name).refdes('#PWR').power_symbol().hide_pin_text()
    d.pin(1).name(name).power()
    s = d.schematic()
    s.pin(1).hidden()
    s.line((0, 0), (0, -50))
    s.line((-50, -50), (50, -50))
    s.line((-25, -75), (25, -75))
    s.line((-5, -100), (5, -100))
    return d
    
def power_flag(l):
    d = l.device('PWR_FLAG').refdes('#FLG').power_symbol().hide_pin_text().hide_name()
    d.pin(1).name('pwr').power_flag()
    s = d.schematic()
    s.pin(1).hidden()
    s.line((0, 0), (0, 25))
    s.line((0, 25), (100, 75), (0, 125), (-100, 75), (0, 25))
    s.text((0, 75), 'PWR').font_size(40)
    return d

def test_point(l):
    d = l.device('Test Point').refdes('TP').hide_pin_text().hide_name()
    d.pin(1).passive()
    s = d.schematic()
    s.pin(1)
    s.circle((0, 0), 20)
    return d

def _passive_2terminal(l, name, refdes):
    d = l.device(name).refdes(refdes).hide_pin_text()
    d.pin(1).passive()
    d.pin(2).passive()
    return d

def resistor(l):
    d = _passive_2terminal(l, 'Resistor', 'R').hide_pin_text()
    s = d.schematic()
    s.pin(1).pos(-100, 0).len(20).dir(kidraw.RIGHT)
    s.pin(2).pos(100, 0).len(20).dir(kidraw.LEFT)
    s.line((-80, 0), (-70, 20), (-60, 0), (-50, -20),
           (-40, 0), (-30, 20), (-20, 0), (-10, -20),
           (0, 0), (10, 20), (20, 0), (30, -20),
           (40, 0), (50, 20), (60, 0), (70, -20),
           (80, 0))
    return d

def capacitor(l, polarized=False):
    n = 'Capacitor (Polarized)' if polarized else 'Capacitor'
    d = _passive_2terminal(l, n, 'C')
    s = d.schematic()
    s.pin(1).pos(-100, 0).len(90).dir(kidraw.RIGHT)
    s.pin(2).pos(100, 0).len(90).dir(kidraw.LEFT)
    s.line((-10, -30), (-10, 30)).width(10)
    s.line((10, -30), (10, 30)).width(10)
    if polarized:
        s.line((20, 20), (30, 20)).width(3)
        s.line((25, 15), (25, 25)).width(3)
    return d

def inductor(l):
    d = _passive_2terminal(l, 'Inductor', 'L').hide_pin_text()
    s = d.schematic()
    s.pin(1).pos(-100, 0).len(20).dir(kidraw.RIGHT)
    s.pin(2).pos(100, 0).len(20).dir(kidraw.LEFT)
    s.arc((-60, 0), 20, 180, 0)
    s.arc((-20, 0), 20, 180, 0)
    s.arc((20, 0), 20, 180, 0)
    s.arc((60, 0), 20, 180, 0)
    return d

def _diode(l, name, refdes='D'):
    d = _passive_2terminal(l, name, refdes).hide_pin_text().hide_name()
    s = d.schematic()
    s.pin(1).pos(-100, 0).len(100).dir(kidraw.RIGHT)
    s.pin(2).pos(100, 0).len(100).dir(kidraw.LEFT)
    s.line((-25, -25), (25, 0), (-25, 25)).filled()
    return d

def diode(l):
    d = _diode(l, 'Diode')
    s = d.schematic()
    s.line((25, -25), (25, 25))
    return d

def zener_diode(l):
    d = _diode(l, 'Zener Diode')
    s = d.schematic()
    s.line((30, -25), (25, -20), (25, 20), (20, 25))
    return d

def schottky_diode(l):
    d = _diode(l, 'Schottky Diode')
    s = d.schematic()
    s.line((15, -15), (15, -25), (25, -25), (25, 25), (35, 25), (35, 15))
    return d

def led(l):
    d = _diode(l, 'LED', refdes='LED')
    s = d.schematic()
    s.line((25, -25), (25, 25))
    with s.save_position():
      s.translate(5, 35).rotate(-60)
      for y in (-8, 8):
          s.line((-12, y), (12, y)).width(3)
          s.line((12, y), (6, y+6)).width(3)
          s.line((12, y), (6, y-6)).width(3)
    return d

def _bjt(l, name='Transistor'):
    d = l.device(name).refdes('Q').hide_pin_text().hide_name()
    s = d.schematic()
    s.circle((0, 0), 70)
    s.line((-20, -50), (-20, 50)).width(10)
    # Base
    s.line((-100, 0), (-20, 0))
    s.text((-95, -20), "B").font_size(20).halign(kidraw.LEFT).valign(kidraw.UP)
    # Collector/Emitter
    s.line((-20, 30), (50, 65))
    s.line((50, 65), (50, 100))
    s.text((60, 100), "C").font_size(20).halign(kidraw.LEFT).valign(kidraw.UP)
    s.line((-20, -30), (50, -65))
    s.line((50, -65), (50, -100))
    s.text((60, -100), "E").font_size(20).halign(kidraw.LEFT).valign(kidraw.DOWN)
    return d

def bipolar_transistor_npn(l):
    d = _bjt(l, name='NPN Bipolar Transistor')
    s = d.schematic()
    with s.save_position():
        s.translate(-20, -30)
        s.rotate(26.56)
        s.line((60, 0), (30, 10), (30, -10)).width(3).filled()
    return d

def bipolar_transistor_pnp(l):
    d = _bjt(l, name='PNP Bipolar Transistor')
    s = d.schematic()
    with s.save_position():
        s.translate(-20, -30)
        s.rotate(26.56)
        s.line((20, 0), (50, 10), (50, -10)).width(3).filled()
    return d

# TODO: JFETs? mosfets?
