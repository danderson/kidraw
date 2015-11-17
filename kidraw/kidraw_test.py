from __future__ import absolute_import
import math
import re
import unittest

import kidraw

class LibraryTest(unittest.TestCase):

    def testEmpty(self):
        l = kidraw.Library()
        self.assertEqual(l.schematic_lib(), '''EESchema-LIBRARY Version 2.3
#encoding utf-8

#End Library''')
        self.assertEqual(l.schematic_doc(), '''EESchema-DOCLIB  Version 2.0
#

#End Doc Library''')
        self.assertEqual(l.footprint_lib(), {})

class DeviceTest(unittest.TestCase):
    def testBasic(self):
        d = kidraw.Device('foo')
        self.assertEqual(d.name, 'foo')
        self.assertEqual(d.doc(), '''$CMP foo
D foo
$ENDCMP''')
        self.assertEqual(d.sch(), '''DEF foo U 0 0 Y Y 1 F N
F0 "U" 0 0 50 H V C BNN
F1 "foo" 0 0 50 H V C TNN
F2 "" 0 0 50 H I C CNN
F3 "" 0 0 50 H I C CNN
DRAW

ENDDRAW
ENDDEF''')

    def testProperties(self):
        d = kidraw.Device('foo')
        d.refdes('F')
        d.description('description')
        d.hide_pin_text()
        d.power_symbol()
        self.assertEqual(d.doc(), '''$CMP foo
D description
$ENDCMP''')
        self.assertEqual(d.sch(), '''DEF foo F 0 0 N N 1 F P
F0 "F" 0 0 50 H I C BNN
F1 "foo" 0 0 50 H V C TNN
F2 "" 0 0 50 H I C CNN
F3 "" 0 0 50 H I C CNN
DRAW

ENDDRAW
ENDDEF''')


class SchematicTest(unittest.TestCase):
    def testBasic(self):
        s = kidraw.Schematic(pins={})
        self.assertEqual(s.sch(), '')

    def testLines(self):
        s = kidraw.Schematic(pins={})
        s.line((0, 0), (10, 10), (15, 10))
        s.line((0, 0), (10, 10), (15, 10)).width(20)
        s.line((0, 0), (10, 10), (15, 10)).filled()
        s.line((0, 0), (10, 10)).width(3).filled()
        self.assertEqual(s.sch(), '''
P 3 0 1 6 0 0 10 10 15 10 N
P 3 0 1 20 0 0 10 10 15 10 N
P 3 0 1 6 0 0 10 10 15 10 F
P 2 0 1 3 0 0 10 10 F
        '''.strip())

    def testRect(self):
        s = kidraw.Schematic(pins={})
        s.rect((-10, -10), (10, 10))
        s.rect((-10, -10), (10, 10)).width(20)
        s.rect((-10, -10), (10, 10)).filled()
        self.assertEqual(s.sch(), '''
P 5 0 1 6 -10 -10 -10 10 10 10 10 -10 -10 -10 N
P 5 0 1 20 -10 -10 -10 10 10 10 10 -10 -10 -10 N
P 5 0 1 6 -10 -10 -10 10 10 10 10 -10 -10 -10 F
        '''.strip())

    def testCircle(self):
        s = kidraw.Schematic(pins={})
        s.circle((0, 0), 20)
        s.circle((1, 1), 20).width(2)
        s.circle((0, 0), 20).filled()
        self.assertEqual(s.sch(), '''
C 0 0 20 0 1 6 N
C 1 1 20 0 1 2 N
C 0 0 20 0 1 6 F
        '''.strip())

    def testArc(self):
        s = kidraw.Schematic(pins={})
        s.arc((0, 0), 20, 30, -30)
        s.arc((1, 1), 20, 30, -30).width(2)
        s.arc((0, 0), 20, 30, -30).filled()
        self.assertEqual(s.sch(), '''
A 0 0 20 300 -300 0 1 6 N 17 10 17 -10
A 1 1 20 300 -300 0 1 2 N 18 11 18 -9
A 0 0 20 300 -300 0 1 6 F 17 10 17 -10
        '''.strip())

    def testText(self):
        s = kidraw.Schematic(pins={})
        s.text((0, 0), 'foo')
        s.text((1, 1), 'foo2').font_size(40)
        s.text((0, 0), 'foo bar').halign(kidraw.RIGHT).valign(kidraw.DOWN)
        self.assertEqual(s.sch(), '''
T 0 0 0 50 0 0 1 "foo" Normal 0 C C
T 0 1 1 40 0 0 1 "foo2" Normal 0 C C
T 0 0 0 50 0 0 1 "foo bar" Normal 0 R D
'''.strip())

    def testPin(self):
        d = kidraw.Device('foo')
        d.pin(1).name('my pin').tristate()
        d.pin(2).name('my pin').passive()
        d.pin(5, 6).name('ground').power()
        d.pin(10).name('flag').power_flag()
        s = d.schematic()
        s.pin(1).dir(kidraw.DOWN)
        s.pin(2).pos(1, 2).len(42).dir(kidraw.LEFT)
        s.pin(5, 6).pos(1, 2).len(42).dir(kidraw.RIGHT).clock()
        s.pin(10).dir(kidraw.UP).active_low().font_size(20)
        self.assertEqual(s.sch(), '''
X my_pin 1 0 0 0 D 50 50 0 1 T 
X my_pin 2 1 2 42 L 50 50 0 1 P 
X ground 5 1 2 42 R 50 50 0 1 W C
X flag 10 0 0 0 U 20 20 0 1 w I
'''.strip())

    def testPinKinds(self):
        d = kidraw.Device('foo')
        d.pin(1).input()
        d.pin(2).output()
        d.pin(3).bidirectional()
        d.pin(4).tristate()
        d.pin(5).passive()
        d.pin(6).open_collector()
        d.pin(7).open_emitter()
        d.pin(8).not_connected()
        d.pin(9).power()
        d.pin(10).power_flag()
        s = d.schematic()
        s.pin(1)
        s.pin(2)
        s.pin(3)
        s.pin(4)
        s.pin(5)
        s.pin(6)
        s.pin(7)
        s.pin(8)
        s.pin(9)
        s.pin(10)
        self.assertEqual(s.sch(), '''
X 1 1 0 0 0 R 50 50 0 1 I 
X 2 2 0 0 0 R 50 50 0 1 O 
X 3 3 0 0 0 R 50 50 0 1 B 
X 4 4 0 0 0 R 50 50 0 1 T 
X 5 5 0 0 0 R 50 50 0 1 P 
X 6 6 0 0 0 R 50 50 0 1 C 
X 7 7 0 0 0 R 50 50 0 1 E 
X 8 8 0 0 0 R 50 50 0 1 N 
X 9 9 0 0 0 R 50 50 0 1 W 
X 10 10 0 0 0 R 50 50 0 1 w 
        '''.strip() + ' ')

    def testPinShapes(self):
        d = kidraw.Device('foo')
        d.pin(1)
        d.pin(2)
        d.pin(3)
        s = d.schematic()
        s.pin(1)
        s.pin(2).active_low()
        s.pin(3).clock()
        self.assertEqual(s.sch(), '''
X 1 1 0 0 0 R 50 50 0 1 U 
X 2 2 0 0 0 R 50 50 0 1 U I
X 3 3 0 0 0 R 50 50 0 1 U C
'''.strip())

        # Disabled for now, because a number of the more complex
        # transforms render surprisingly.

#     def testTransform(self):
#         d = kidraw.Device('foo')
#         d.pin(1)
#         s = d.schematic()
#         s.translate(10, 10)
#         s.rotate(-90)
#         s.scale(2, 2)
#         s.pin(1).pos(2, 2)
#         s.line((0, 0), (1, 1))
#         s.rect((0, 0), (1, 1))
#         s.circle((0, 0), 20)
#         s.arc((0, 0), 20, 30, -30)
#         s.text((0, 0), 'test')
#         self.assertEqual(s.sch(), '''
# X 1 1 6 14 0 R 50 50 0 1 U 
# P 2 0 1 6 10 10 8 12 N
# P 5 0 1 6 10 10 8 10 8 12 10 12 10 10 N
# C 10 10 20 0 1 6 N
# A 10 10 20 -600 -1200 0 1 6 N -10 45 30 45
# T 0 10 10 50 0 0 1 "test" Normal 0 C C
# '''.strip())

def _sexpr(expr):
    return re.sub(r'[ \n]+', '\n', expr.strip())

class FootprintTest(unittest.TestCase):
    def _assertSExpr(self, a, b):
        self.maxDiff = None
        self.assertEqual(_sexpr(a), _sexpr(b))

    def testBasic(self):
        f = kidraw.Footprint('test footprint', {})
        self._assertSExpr(f.footprint(), '(module test_footprint (layer F.Cu) (tedit 0) )')

    def testFootprintDefaults(self):
        f = kidraw.Footprint('test footprint', {})
        f.mask_margin(20)
        f.paste_margin(50)
        f.clearance(42)
        self._assertSExpr(f.footprint(), '''
(module test_footprint
  (layer F.Cu)
  (tedit 0)
  (solder_mask_margin 20)
  (solder_paste_margin -50)
  (clearance 42)
)
        ''')

    def testText(self):
        f = kidraw.Footprint('test', {})
        f.text('foo')
        f.text('bar').pos(10, 10).size(20, 20).thickness(2)
        self._assertSExpr(f.footprint(), '''
(module test
  (layer F.Cu)
  (tedit 0)
  (fp_text user "foo" 
    (at 0 0)
    (layer F.SilkS)
  )
  (fp_text user "bar"
    (at 10 10)
    (layer F.SilkS)
    (effects
      (font
        (size 20 20)
        (thickness 2)
      )
    )
  )
)
        ''')

        f = kidraw.Footprint('test', {})
        f.refdes().pos(10, 10).size(20, 20).thickness(2)
        f.value().pos(10, 10).size(20, 20).thickness(2)
        self._assertSExpr(f.footprint(), '''
(module test
  (layer F.Cu)
  (tedit 0)
  (fp_text reference "REFDES"
    (at 10 10)
    (layer F.SilkS)
    (effects
      (font
        (size 20 20)
        (thickness 2)
      )
    )
  )
  (fp_text value "VALUE"
    (at 10 10)
    (layer F.SilkS)
    (effects
      (font
        (size 20 20)
        (thickness 2)
      )
    )
  )
)
''')

    def testLine(self):
        f = kidraw.Footprint('test', {})
        f.line((0, 0), (10, 10))
        f.line((10, 10), (20, 20)).width(12)
        self._assertSExpr(f.footprint(), '''
(module test
  (layer F.Cu)
  (tedit 0)
  (fp_line
    (layer F.SilkS)
    (start 0 0)
    (end 10 10)
    (width 0)
  )
  (fp_line
    (layer F.SilkS)
    (start 10 10)
    (end 20 20)
    (width 12)
  )
)
''')

    def testCircle(self):
        f = kidraw.Footprint('test', {})
        f.circle((0, 0), 10)
        f.circle((10, 10), 2).width(12)
        self._assertSExpr(f.footprint(), '''
(module test
  (layer F.Cu)
  (tedit 0)
  (fp_circle
    (layer F.SilkS)
    (center 0 0)
    (end 10 0)
    (width 0)
  )
  (fp_circle
    (layer F.SilkS)
    (center 10 10)
    (end 12 10)
    (width 12)
  )
)
''')

    def testPin(self):
        d = kidraw.Device('test')
        d.pin(1)
        d.pin(2)
        d.pin(3, 4)
        f = d.footprint('foo')
        f.pad(1).pos(10, 10).smd().rect(5, 5)
        f.pad(2).pos(-10, 10).thruhole(4).circle(9)
        f.pad(3).pos(-10, -10).thruhole(3).oval(10, 5).mask_margin(1).paste_margin(3)
        f.pad(4).pos(10, -10).test_point().circle(20).clearance(2)
        self._assertSExpr(f.footprint(), '''
(module foo
  (layer F.Cu)
  (tedit 0)
  (pad 1 smd circle
    (at 10 10)
    (size 5 5)
    (layers F.Cu F.Paste F.Mask F.SilkS)
  )
  (pad 2 thru_hole circle
    (at -10 10)
    (size 9 9)
    (layers *.Cu *.Mask F.SilkS)
    (drill 4)
  )
  (pad 3 thru_hole circle
    (at -10 -10)
    (size 10 5)
    (layers *.Cu *.Mask F.SilkS)
    (drill 3)
    (solder_mask_margin 1)
    (solder_paste_margin -3)
  )
  (pad 4 connector circle
    (at 10 -10)
    (size 20 20)
    (layers F.Cu F.Paste F.Mask F.SilkS)
    (clearance 2)
  )
)
'''.strip())

class TransformTest(unittest.TestCase):
    def testIdentity(self):
        t = kidraw.Transform()
        self.assertEqual(t.coords(0, 0), (0, 0))
        self.assertEqual(t.coords(1, 2), (1, 2))
        self.assertEqual(t.fcoords(0, 0), (0.0, 0.0))
        self.assertEqual(t.fcoords(4.5, 3.5), (4.5, 3.5))
        self.assertEqual(t.angle(45), 45)
        self.assertEqual(t.angle(190), -170)

    def testTranslate(self):
        t = kidraw.Transform()
        t.translate(5, 10)
        self.assertEqual(t.coords(0, 0), (5, 10))
        self.assertEqual(t.coords(2, 4), (7, 14))
        self.assertEqual(t.fcoords(0, 0), (5.0, 10.0))
        self.assertEqual(t.fcoords(2.5, 4.5), (7.5, 14.5))
        self.assertEqual(t.angle(45), 45)
        
    def testRotate(self):
        t = kidraw.Transform()
        # 90 degrees CCW
        t.rotate(-90)
        self.assertEqual(t.coords(0, 0), (0, 0))
        self.assertEqual(t.coords(1, 0), (0, 1))
        self.assertEqual(t.coords(1, 1), (-1, 1))
        self.assertEqual(t.fcoords(1.1, 1.4), (-1.4, 1.1))
        self.assertEqual(t.angle(45), -45)
        t.rotate(45)
        x, y = t.fcoords(1, 1)
        self.assertAlmostEqual(x, 0.0)
        self.assertAlmostEqual(y, math.sqrt(2))
        self.assertEqual(t.coords(1, 1), (0, 1))
        self.assertEqual(t.angle(45), 0)

    def testScale(self):
        t = kidraw.Transform()
        t.scale(0.5, 2)
        self.assertEqual(t.coords(2, 2), (1, 4))
        x, y = t.fcoords(1, 1.2)
        self.assertAlmostEqual(x, 0.5)
        self.assertAlmostEqual(y, 2.4)
        self.assertEqual(t.angle(45), 45)

    def testCombined(self):
        t = kidraw.Transform()
        t.translate(10, 10)
        t.rotate(-135)
        t.scale(0.5, 0.5)
        t.translate(0, math.sqrt(200))
        x, y = t.fcoords(0, math.sqrt(200))
        self.assertAlmostEqual(x, 0)
        self.assertAlmostEqual(y, 0)
        x, y = t.fcoords(0, 2*math.sqrt(200))
        self.assertAlmostEqual(x, -5)
        self.assertAlmostEqual(y, -5)
        self.assertEqual(t.angle(-45), -180)

    def testPushPop(self):
        t = kidraw.Transform()
        self.assertEqual(t.coords(10, 10), (10, 10))
        self.assertEqual(t.angle(45), 45)
        t.push()
        t.translate(10, 10)
        t.rotate(180)
        self.assertEqual(t.coords(10, 10), (0, 0))
        self.assertEqual(t.angle(45), -135)
        t.pop()
        self.assertEqual(t.coords(10, 10), (10, 10))
        self.assertEqual(t.angle(45), 45)

    def testBoundingBox(self):
        t = kidraw.Transform()
        self.assertEqual(t.x_min, 0)
        self.assertEqual(t.x_max, 0)
        self.assertEqual(t.y_min, 0)
        self.assertEqual(t.y_max, 0)
        t.boundingbox(10, 10)
        self.assertEqual(t.x_min, 0)
        self.assertEqual(t.x_max, 10)
        self.assertEqual(t.y_min, 0)
        self.assertEqual(t.y_max, 10)
        t.boundingbox(5, 5)
        self.assertEqual(t.x_min, 0)
        self.assertEqual(t.x_max, 10)
        self.assertEqual(t.y_min, 0)
        self.assertEqual(t.y_max, 10)
        t.boundingbox(-5, -5)
        self.assertEqual(t.x_min, -5)
        self.assertEqual(t.x_max, 10)
        self.assertEqual(t.y_min, -5)
        self.assertEqual(t.y_max, 10)
        
    def testBoundingBoxTransform(self):
        t = kidraw.Transform()
        t.translate(10, 10)
        t.boundingbox(10, 10)
        self.assertEqual(t.x_min, 0)
        self.assertEqual(t.x_max, 20)
        self.assertEqual(t.y_min, 0)
        self.assertEqual(t.y_max, 20)

