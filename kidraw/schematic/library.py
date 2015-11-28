def vcc(name='VCC'):
    s = Schematic(name=name,
                  refdes='#PWR',
                  description='{0} power rail'.format(name),
                  show_pin_text=False,
                  show_refdes=False,
                  power_symbol=True)
    s.features = [
        Line(points=[(0, 0), (0, 50)]),
        Line(points=[(-50, 50), (50, 50)]),
        Pin(numbers=1, name=name, type=Pin.Power, shape=Pin.Hidden),
    ]
    s.name.pos = (0, 100)
    return s

def gnd(name='GND'):
    s = Schematic(name=name,
                  refdes='#PWR',
                  description='{0} ground rail'.format(name),
                  show_pin_text=False,
                  show_refdes=False,
                  power_symbol=True)
    s.features = [
        Line(points=[(0, 0), (0, -50)]),
        Line(points=[(-50, -50), (50, -50)]),
        Line(points=[(-25, -75), (25, -75)]),
        Line(points=[(-5, -100), (5, -100)]),
        Pin(numbers=1, name=name, type=Pin.Power, shape=Pin.Hidden),
    ]
    s.name.pos = (0, -150)
    return s

def power_flag():
    s = Schematic(name='PWR_FLAG',
                  refdes='#FLG',
                  hide_pin_text=True,
                  hide_name=True,
                  power_symbol=True)
    s.features = [
        Line(points=[(0, 0), (0, 25)]),
        Line(points=[(0, 25), (100, 75), (0, 125), (-100, 75), (0, 25)]),
        Text(pos=(0, 75), text='PWR', font_size=40),
        Pin(numbers=1, name=name, type=Pin.PowerFlag, shape=Pin.Hidden),
    ]
    return s

def test_point():
    s = Schematic(name='Test Point',
                  refdes='TP',
                  hide_pin_text=True,
                  hide_name=True)
    s.features = [
        Pin(numbers=1, type=Pin.Passive),
        Circle(center=(0, 0), radius=20),
    ]
    return s

def resistor():
    s = Schematic(name='Resistor',
                  refdes='R',
                  hide_pin_text=True)
    s.features = [
        Pin(numbers=1, pos=(-100, 0), len=20, dir=Pin.Right, type=Pin.Passive),
        Pin(numbers=2, pos=(100, 0), len=20, dir=Pin.Right, type=Pin.Passive),
        Line(points=[
            (-80, 0), (-70, 20), (-60, 0), (-50, -20),
            (-40, 0), (-30, 20), (-20, 0), (-10, -20),
            (0, 0), (10, 20), (20, 0), (30, -20),
            (40, 0), (50, 20), (60, 0), (70, -20),
            (80, 0)
        ]),
    ]
    return s

def capacitor(polarized):
    s = Schematic(name='Capacitor',
                  refdes='C',
                  hide_pin_text=True)
    s.features = [
        Pin(numbers=1, pos=(-100, 0), len=90, dir=Pin.Right, type=Pin.Passive),
        Pin(numbers=2, pos=(100, 0), len=90, dir=Pin.Left, type=Pin.Passive),
        Line(points=[(-10, -30), (-10, 30)], width=10),
        Line(points=[(10, -30), (10, 30)], width=10),
    ]
    if polarized:
        s.name += ' (Polarized)'
        s.features += [
            Line(points=[(20, 20), (30, 20)], width=3),
            Line(points=[(25, 15), (25, 25)], width=3),
        ]
    return s

def inductor():
    s = Schematic(name='Inductor',
                  refdes='L',
                  hide_pin_text=True)
    s.features = [
        Pin(numbers=1, pos=(-100, 0), len=20, dir=Pin.Right, type=Pin.Passive),
        Pin(numbers=2, pos=(100, 0), len=20, dir=Pin.Left, type=Pin.Passive),
        Arc(center=(-60, 0), radius=20, angle_start=180, angle_end=0),
        Arc(center=(-20, 0), radius=20, angle_start=180, angle_end=0),
        Arc(center=(20, 0), radius=20, angle_start=180, angle_end=0),
        Arc(center=(60, 0), radius=20, angle_start=180, angle_end=0),
    ]
    return s

def diode():
    s = Schematic(name='Diode',
                  refdes='D',
                  hide_pin_text=True,
                  hide_name=True)
    s.features = [
        Pin(numbers=1, pos=(-100, 0), len=100, dir=Pin.Right, type=Pin.Passive),
        Pin(numbers=2, pos=(100, 0), len=100, dir=Pin.Left, type=Pin.Passive),
        Line(points=[(-25, -25), (25, 0), (-25, 25)], filled=True),
        Line(points=[(25, -25), (25, 25)]),
    ]
    return s        

def zener_diode():
    s = Schematic(name='Zener Diode',
                  refdes='D',
                  hide_pin_text=True,
                  hide_name=True)
    s.features = [
        Pin(numbers=1, pos=(-100, 0), len=100, dir=Pin.Right, type=Pin.Passive),
        Pin(numbers=2, pos=(100, 0), len=100, dir=Pin.Left, type=Pin.Passive),
        Line(points=[(-25, -25), (25, 0), (-25, 25)], filled=True),
        Line(points=[(30, -25), (25, -20), (25, 20), (20, 25)])
    ]
    return s

def schottky_diode():
    s = Schematic(name='Schottky Diode',
                  refdes='D',
                  hide_pin_text=True,
                  hide_name=True)
    s.features = [
        Pin(numbers=1, pos=(-100, 0), len=100, dir=Pin.Right, type=Pin.Passive),
        Pin(numbers=2, pos=(100, 0), len=100, dir=Pin.Left, type=Pin.Passive),
        Line(points=[(-25, -25), (25, 0), (-25, 25)], filled=True),
        Line(points=[(15, -15), (15, -25), (25, -25), (25, 25), (35, 25), (35, 15)]),
    ]
    return s

def led():
    s = Schematic(name='LED',
                  refdes='LED',
                  hide_pin_text=True,
                  hide_name=True)
    s.features = [
        Pin(numbers=1, pos=(-100, 0), len=100, dir=Pin.Right, type=Pin.Passive),
        Pin(numbers=2, pos=(100, 0), len=100, dir=Pin.Left, type=Pin.Passive),
        Line(points=[(-25, -25), (25, 0), (-25, 25)], filled=True),
        Line(points=[(25, -25), (25, 25)]),

        # LED arrows
        Line(points=[(6, 21), (18, 41)]),
        Line(points=[(18, 41), (10, 39)]),
        Line(points=[(18, 41), (20, 33)]),
        Line(points=[(-8, 29), (4, 49)]),
        Line(points=[(4, 49), (-4, 47)]),
        Line(points=[(4, 49), (6, 41)]),
    ]
    return s

def switch():
    s = Schematic(name='Switch SPST',
                  refdes='S',
                  hide_pin_text=True,
                  hide_name=True)
    s.features = [
        Pin(numbers=1, pos=(-100, 0), len=50, dir=Pin.Right, type=Pin.Passive),
        Pin(numbers=2, pos=(100, 0), len=50, dir=Pin.Left, type=Pin.Passive),
        Line(points=[(-50, 0), (50, 50)]),
    ]
    return s
