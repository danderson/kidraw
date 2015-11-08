#!/usr/bin/env python

from kidraw import *

with library('stdlib') as l:
    l.std.resistor()
    l.std.capacitor()
    l.std.capacitor.polarized()
    l.std.inductor()
    l.std.diode()
    l.std.diode.zener()
    l.std.diode.schottky()
    l.std.led()
