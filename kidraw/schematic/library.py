from kidraw import schematic as sch

def vcc(name='VCC'):
    s = sch.Schematic(name=name,
                      refdes='#PWR',
                      description='{0} power rail'.format(name),
                      show_pin_text=False,
                      show_refdes=False,
                      power_symbol=True)
    s.features = [
        sch.Line(points=[(0, 0), (0, 50)]),
        sch.Line(points=[(-50, 50), (50, 50)]),
        sch.Pin(numbers=1, name=name, type=sch.Pin.Power, shape=sch.Pin.Hidden),
    ]
    s.name.pos = (0, 100)
    return s

def gnd(name='GND'):
    s = sch.Schematic(name=name,
                      refdes='#PWR',
                      description='{0} ground rail'.format(name),
                      show_pin_text=False,
                      show_refdes=False,
                      power_symbol=True)
    s.features = [
        sch.Line(points=[(0, 0), (0, -50)]),
        sch.Line(points=[(-50, -50), (50, -50)]),
        sch.Line(points=[(-25, -75), (25, -75)]),
        sch.Line(points=[(-5, -100), (5, -100)]),
        sch.Pin(numbers=1, name=name, type=sch.Pin.Power, shape=sch.Pin.Hidden),
    ]
    s.name.pos = (0, -150)
    return s

def power_flag():
    s = sch.Schematic(name='PWR_FLAG',
                      refdes='#FLG',
                      show_pin_text=False,
                      show_name=False,
                      show_refdes=False,
                      power_symbol=True)
    s.features = [
        sch.Line(points=[(0, 0), (0, 25)]),
        sch.Line(points=[(0, 25), (100, 75), (0, 125), (-100, 75), (0, 25)]),
        sch.Text(pos=(0, 75), text='PWR', font_size=40),
        sch.Pin(numbers=1, name='pwd', type=sch.Pin.PowerFlag, shape=sch.Pin.Hidden),
    ]
    return s

def test_point():
    s = sch.Schematic(name='Test Point',
                      refdes='TP',
                      show_pin_text=False,
                      show_name=False)
    s.features = [
        sch.Pin(numbers=1, type=sch.Pin.Passive),
        sch.Circle(center=(0, 0), radius=20),
    ]
    return s

def resistor():
    s = sch.Schematic(name='Resistor',
                      refdes='R',
                      show_pin_text=False)
    s.features = [
        sch.Pin(numbers=1, pos=(-100, 0), len=20, dir=sch.Pin.Right, type=sch.Pin.Passive),
        sch.Pin(numbers=2, pos=(100, 0), len=20, dir=sch.Pin.Left, type=sch.Pin.Passive),
        sch.Line(points=[
            (-80, 0), (-70, 20), (-60, 0), (-50, -20),
            (-40, 0), (-30, 20), (-20, 0), (-10, -20),
            (0, 0), (10, 20), (20, 0), (30, -20),
            (40, 0), (50, 20), (60, 0), (70, -20),
            (80, 0)
        ]),
    ]
    return s

def capacitor(polarized=False):
    s = sch.Schematic(name='Capacitor',
                      refdes='C',
                      show_pin_text=False)
    s.features = [
        sch.Pin(numbers=1, pos=(-100, 0), len=90, dir=sch.Pin.Right, type=sch.Pin.Passive),
        sch.Pin(numbers=2, pos=(100, 0), len=90, dir=sch.Pin.Left, type=sch.Pin.Passive),
        sch.Line(points=[(-10, -30), (-10, 30)], width=10),
        sch.Line(points=[(10, -30), (10, 30)], width=10),
    ]
    if polarized:
        s.name.text += ' (Polarized)'
        s.features += [
            sch.Line(points=[(20, 20), (30, 20)], width=3),
            sch.Line(points=[(25, 15), (25, 25)], width=3),
        ]
    return s

def inductor():
    s = sch.Schematic(name='Inductor',
                      refdes='L',
                      show_pin_text=False)
    s.features = [
        sch.Pin(numbers=1, pos=(-100, 0), len=20, dir=sch.Pin.Right, type=sch.Pin.Passive),
        sch.Pin(numbers=2, pos=(100, 0), len=20, dir=sch.Pin.Left, type=sch.Pin.Passive),
        sch.Arc(center=(-60, 0), radius=20, angle_start=180, angle_end=0),
        sch.Arc(center=(-20, 0), radius=20, angle_start=180, angle_end=0),
        sch.Arc(center=(20, 0), radius=20, angle_start=180, angle_end=0),
        sch.Arc(center=(60, 0), radius=20, angle_start=180, angle_end=0),
    ]
    return s

def diode():
    s = sch.Schematic(name='Diode',
                      refdes='D',
                      show_pin_text=False,
                      show_name=False)
    s.features = [
        sch.Pin(numbers=1, pos=(-100, 0), len=100, dir=sch.Pin.Right, type=sch.Pin.Passive),
        sch.Pin(numbers=2, pos=(100, 0), len=100, dir=sch.Pin.Left, type=sch.Pin.Passive),
        sch.Line(points=[(-25, -25), (25, 0), (-25, 25)], filled=True),
        sch.Line(points=[(25, -25), (25, 25)]),
    ]
    return s        

def zener_diode():
    s = sch.Schematic(name='Zener Diode',
                      refdes='D',
                      show_pin_text=False,
                      show_name=False)
    s.features = [
        sch.Pin(numbers=1, pos=(-100, 0), len=100, dir=sch.Pin.Right, type=sch.Pin.Passive),
        sch.Pin(numbers=2, pos=(100, 0), len=100, dir=sch.Pin.Left, type=sch.Pin.Passive),
        sch.Line(points=[(-25, -25), (25, 0), (-25, 25)], filled=True),
        sch.Line(points=[(30, -25), (25, -20), (25, 20), (20, 25)])
    ]
    return s

def schottky_diode():
    s = sch.Schematic(name='Schottky Diode',
                      refdes='D',
                      show_pin_text=False,
                      show_name=False)
    s.features = [
        sch.Pin(numbers=1, pos=(-100, 0), len=100, dir=sch.Pin.Right, type=sch.Pin.Passive),
        sch.Pin(numbers=2, pos=(100, 0), len=100, dir=sch.Pin.Left, type=sch.Pin.Passive),
        sch.Line(points=[(-25, -25), (25, 0), (-25, 25)], filled=True),
        sch.Line(points=[(15, -15), (15, -25), (25, -25), (25, 25), (35, 25), (35, 15)]),
    ]
    return s

def led():
    s = sch.Schematic(name='LED',
                      refdes='LED',
                      show_pin_text=False,
                      show_name=False)
    s.features = [
        sch.Pin(numbers=1, pos=(-100, 0), len=100, dir=sch.Pin.Right, type=sch.Pin.Passive),
        sch.Pin(numbers=2, pos=(100, 0), len=100, dir=sch.Pin.Left, type=sch.Pin.Passive),
        sch.Line(points=[(-25, -25), (25, 0), (-25, 25)], filled=True),
        sch.Line(points=[(25, -25), (25, 25)]),

        # LED arrows
        sch.Line(points=[(6, 21), (18, 41)]),
        sch.Line(points=[(18, 41), (10, 39)]),
        sch.Line(points=[(18, 41), (20, 33)]),
        sch.Line(points=[(-8, 29), (4, 49)]),
        sch.Line(points=[(4, 49), (-4, 47)]),
        sch.Line(points=[(4, 49), (6, 41)]),
    ]
    return s

def switch():
    s = sch.Schematic(name='Switch SPST',
                      refdes='S',
                      show_pin_text=False,
                      show_name=False)
    s.features = [
        sch.Pin(numbers=1, pos=(-100, 0), len=50, dir=sch.Pin.Right, type=sch.Pin.Passive),
        sch.Pin(numbers=2, pos=(100, 0), len=50, dir=sch.Pin.Left, type=sch.Pin.Passive),
        sch.Line(points=[(-50, 0), (50, 50)]),
    ]
    return s
