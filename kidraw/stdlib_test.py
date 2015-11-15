import unittest
import kidraw
from kidraw import stdlib as std

class TestStdlib(unittest.TestCase):
    def testBuild(self):
        l = kidraw.Library()
        std.vcc(l)
        std.vcc(l, '+5V')
        std.gnd(l)
        std.gnd(l, 'AGND')
        std.power_flag(l)
        
        std.resistor(l)
        std.capacitor(l)
        std.capacitor(l, polarized=True)
        std.inductor(l)
        std.diode(l)
        std.zener_diode(l)
        std.schottky_diode(l)
        std.led(l)
        std.bipolar_transistor_npn(l)
        std.bipolar_transistor_pnp(l)
