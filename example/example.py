#!/usr/bin/env python

import kidraw
from kidraw import ipc
from kidraw import schematic as sch
from kidraw.footprint import library as flib
from kidraw.schematic import library as slib

lib = kidraw.Library("example")

lib.devices = [
    kidraw.Device(slib.vcc("+5V")),
    kidraw.Device(slib.vcc("+12V")),
    kidraw.Device(slib.gnd()),
    kidraw.Device(slib.power_flag()),

    kidraw.Device(
        schematic=slib.resistor(),
        footprints=[
            flib.chip(flib.imperial("0805")),
            flib.chip(flib.imperial("1206")),
        ]),
    kidraw.Device(
        schematic=slib.capacitor(),
        footprints=[
            flib.chip(flib.imperial("0603")),
            flib.chip(flib.imperial("1206")),
        ]),
    kidraw.Device(
        schematic=slib.capacitor(polarized=True),
        footprints=[
            flib.chip(flib.imperial("0805"), polarized=True),
            flib.chip(flib.imperial("1206"), polarized=True),
        ]),
    kidraw.Device(
        schematic=slib.inductor(),
        footprints=[
            flib.chip(flib.imperial("1206")),
        ]),
    kidraw.Device(
        schematic=slib.led(),
        footprints=[
            flib.chip(flib.imperial("1206")),
        ]),
]

s = sch.Schematic(name="STM32F042K6T6",
                  description="ARM Cortex M0 microcontroller")
with sch.ICBuilder(s, 32, pin_len=300) as ic:
    ic.side(sch.Pin.Left)
    ic.pin([1, 5, 17], name="VDD", type=sch.Pin.Power)
    ic.gap(1)
    ic.pin(4, name="~RST", type=sch.Pin.Input)
    ic.pin(31, name="BOOT", type=sch.Pin.Input)
    ic.gap(1)
    ic.pin(21, name="USB_D-", type=sch.Pin.Bidirectional)
    ic.pin(22, name="USB_D+", type=sch.Pin.Bidirectional)
    ic.gap(1)
    ic.pin(23, name="SWDIO", type=sch.Pin.Bidirectional)
    ic.pin(24, name="SWCLK", type=sch.Pin.Bidirectional)
    ic.gap(1)
    ic.pin([16, 32], name="VSS", type=sch.Pin.Power)

    ic.side(sch.Pin.Right)
    for i in range(4):
        ic.pin(numbers=6 + i, name=f"PWM2_{i + 1}", type=sch.Pin.Bidirectional)
    ic.pin(numbers=10, name="PWM14", type=sch.Pin.Bidirectional)
    for i in range(4):
        ic.pin(numbers=12 + i, name=f"PWM3_{i + 1}", type=sch.Pin.Bidirectional)
    for i in range(3):
        ic.pin(numbers=18 + i, name=f"PWM3_{i + 1}", type=sch.Pin.Bidirectional)
lib.devices.append(
    kidraw.Device(
        schematic=s,
        footprints=[
            flib.QFP(
                A=ipc.Dimension(6.8, 7.2),
                L=ipc.Dimension(8.8, 9.2),
                T=ipc.Dimension(0.45, 0.75),
                W=ipc.Dimension(0.3, 0.45),
                pitch=0.8,
                num_pins=32),
        ]))

s = sch.Schematic(name="AP2120N",
                  description="3.3V linear regulator")
with sch.ICBuilder(s, 3, slot_spacing=50) as ic:
    ic.side(sch.Pin.Left)
    ic.pin(3, name="Vin", type=sch.Pin.Power)
    ic.side(sch.Pin.Down)
    ic.pin(1, name="GND", type=sch.Pin.Power)
    ic.side(sch.Pin.Right)
    ic.pin(2, name="Vout", type=sch.Pin.Power)
lib.devices.append(kidraw.Device(schematic=s, footprints=[flib.SOT23(3)]))

lib.save()
