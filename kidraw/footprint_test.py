from kidraw import footprint as fp
import unittest

def CanonicalizeSExpr(s):
    lines = s.splitlines()
    lines = [s.split('#', 1)[0].strip() for s in lines]
    s = ' '.join(lines)
    s = s.replace('(', '\n(').replace(')', ')\n')
    lines = s.splitlines()
    lines = [s.strip() for s in lines]
    return '\n'.join(lines).strip()

class FootprintTest(unittest.TestCase):
    def assertSExpr(self, a, b):
        self.assertMultiLineEqual(CanonicalizeSExpr(a), CanonicalizeSExpr(b))

    def testText(self):
        t = fp.Text(text='test')
        self.assertSExpr(str(t), '(fp_text user "test" (at 0 0) (layer F.SilkS) (effects (font (size 1 1) (thickness 0.15))))')

        t.position = (1, 1.5)
        self.assertSExpr(str(t), '(fp_text user "test" (at 1 1.5) (layer F.SilkS) (effects (font (size 1 1) (thickness 0.15))))')

        t.layer = fp.Layer.BottomAssembly
        self.assertSExpr(str(t), '(fp_text user "test" (at 1 1.5) (layer B.Fab) (effects (font (size 1 1) (thickness 0.15))))')

        t.hidden = True
        self.assertSExpr(str(t), '(fp_text user "test" (at 1 1.5) (layer B.Fab) hide (effects (font (size 1 1) (thickness 0.15))))')

        t.font_size = (1.5, 2.6)
        t.line_width = 42
        self.assertSExpr(str(t), '(fp_text user "test" (at 1 1.5) (layer B.Fab) hide (effects (font (size 1.5 2.6) (thickness 42))))')

    def testLine(self):
        t = fp.Line()
        self.assertSExpr(str(t), '(fp_line (start 0 0) (end 0 0) (layer F.SilkS) (width 0.15))')

        t.start = (1.5, 2.6)
        self.assertSExpr(str(t), '(fp_line (start 1.5 2.6) (end 0 0) (layer F.SilkS) (width 0.15))')

        t.end = (42, -60)
        self.assertSExpr(str(t), '(fp_line (start 1.5 2.6) (end 42 -60) (layer F.SilkS) (width 0.15))')

        t.layer = fp.Layer.BottomCopper
        self.assertSExpr(str(t), '(fp_line (start 1.5 2.6) (end 42 -60) (layer B.Cu) (width 0.15))')

        t.line_width = 0.5
        self.assertSExpr(str(t), '(fp_line (start 1.5 2.6) (end 42 -60) (layer B.Cu) (width 0.5))')

    def testCircle(self):
        t = fp.Circle()
        self.assertSExpr(str(t), '(fp_circle (center 0 0) (end 0 0) (layer F.SilkS) (width 0.15))')

        t.center = (1.5, 2.6)
        self.assertSExpr(str(t), '(fp_circle (center 1.5 2.6) (end 1.5 2.6) (layer F.SilkS) (width 0.15))')

        t.radius = 4
        self.assertSExpr(str(t), '(fp_circle (center 1.5 2.6) (end 5.5 2.6) (layer F.SilkS) (width 0.15))')

        t.layer = fp.Layer.TopSolderMask
        self.assertSExpr(str(t), '(fp_circle (center 1.5 2.6) (end 5.5 2.6) (layer F.Mask) (width 0.15))')

        t.line_width = 0.1
        self.assertSExpr(str(t), '(fp_circle (center 1.5 2.6) (end 5.5 2.6) (layer F.Mask) (width 0.1))')

    def testArc(self):
        t = fp.Arc()
        self.assertSExpr(str(t), '(fp_arc (start 0 0) (end 0.0 0.0) (angle 0) (layer F.SilkS) (width 0.15))')

        t.center = (3, 4)
        t.radius = 10
        t.start_angle = 0
        t.end_angle = 45
        self.assertSExpr(str(t), '(fp_arc (start 3 4) (end 3.0 14.0) (angle 45) (layer F.SilkS) (width 0.15))')

        t.start_angle = 90
        t.end_angle = 135
        self.assertSExpr(str(t), '(fp_arc (start 3 4) (end 13.0 4.0) (angle 45) (layer F.SilkS) (width 0.15))')

        t.layer = fp.Layer.TopPasteMask
        self.assertSExpr(str(t), '(fp_arc (start 3 4) (end 13.0 4.0) (angle 45) (layer F.Paste) (width 0.15))')

        t.line_width = 0.1
        self.assertSExpr(str(t), '(fp_arc (start 3 4) (end 13.0 4.0) (angle 45) (layer F.Paste) (width 0.1))')

    def testPoly(self):
        t = fp.Poly()
        self.assertSExpr(str(t), '(fp_poly (pts  ) (layer F.SilkS) (width 0.15))')

        t.points = [(0, 0), (1, 1), (1.5, 2.6)]
        self.assertSExpr(str(t), '(fp_poly (pts (xy 0 0) (xy 1 1) (xy 1.5 2.6)) (layer F.SilkS) (width 0.15))')

        t.layer = fp.Layer.TopCourtyard
        self.assertSExpr(str(t), '(fp_poly (pts (xy 0 0) (xy 1 1) (xy 1.5 2.6)) (layer F.CrtYd) (width 0.15))')

        t.line_width = 0.1
        self.assertSExpr(str(t), '(fp_poly (pts (xy 0 0) (xy 1 1) (xy 1.5 2.6)) (layer F.CrtYd) (width 0.1))')

    def testThroughHole(self):
        p = fp.ThroughHolePad()
        self.assertSExpr(str(p), '''(pad 0 thru_hole circle
  (at 0 0 0)
  (size 0 0)
  (drill 0)
  (layers *.Cu *.Mask F.SilkS)
  (solder_mask_margin 0)
  (clearance 0)
)''')

        p.name = 42
        p.shape = fp.PadShape.Obround
        self.assertSExpr(str(p), '''(pad 42 thru_hole oval
  (at 0 0 0)
  (size 0 0)
  (drill 0)
  (layers *.Cu *.Mask F.SilkS)
  (solder_mask_margin 0)
  (clearance 0)
)''')

        p.center = (1.5, 2.6)
        p.angle = 42.42
        p.size = (10, 20)
        self.assertSExpr(str(p), '''(pad 42 thru_hole oval
  (at 1.5 2.6 42.42)
  (size 10 20)
  (drill 0)
  (layers *.Cu *.Mask F.SilkS)
  (solder_mask_margin 0)
  (clearance 0)
)''')

        p.drill_size = 5
        self.assertSExpr(str(p), '''(pad 42 thru_hole oval
  (at 1.5 2.6 42.42)
  (size 10 20)
  (drill 5)
  (layers *.Cu *.Mask F.SilkS)
  (solder_mask_margin 0)
  (clearance 0)
)''')
        
        p.clearance = 1
        p.solder_mask_margin = 2
        self.assertSExpr(str(p), '''(pad 42 thru_hole oval
  (at 1.5 2.6 42.42)
  (size 10 20)
  (drill 5)
  (layers *.Cu *.Mask F.SilkS)
  (solder_mask_margin 2)
  (clearance 1)
)''')

        p.thermal_width = 1.2
        p.thermal_gap = 2.3
        self.assertSExpr(str(p), '''(pad 42 thru_hole oval
  (at 1.5 2.6 42.42)
  (size 10 20)
  (drill 5)
  (layers *.Cu *.Mask F.SilkS)
  (solder_mask_margin 2)
  (clearance 1)
  (zone_connect 1)
  (thermal_width 1.2)
  (thermal_gap 2.3)
)''')

    def testSurfaceMount(self):
        p = fp.SurfaceMountPad()
        self.assertSExpr(str(p), '''(pad 0 smd rect
  (at 0 0 0)
  (size 0 0)
  (layers F.Cu F.Paste F.Mask)
  (solder_mask_margin 0)
  (clearance 0)
  (solder_paste_margin 0)
  (solder_paste_ratio 0)
)''')

        p.name = 42
        p.shape = fp.PadShape.Circle
        self.assertSExpr(str(p), '''(pad 42 smd circle
  (at 0 0 0)
  (size 0 0)
  (layers F.Cu F.Paste F.Mask)
  (solder_mask_margin 0)
  (clearance 0)
  (solder_paste_margin 0)
  (solder_paste_ratio 0)
)''')
        
        p.center = (1.5, 2.6)
        p.angle = 42
        p.size = (4, 4)
        self.assertSExpr(str(p), '''(pad 42 smd circle
  (at 1.5 2.6 42)
  (size 4 4)
  (layers F.Cu F.Paste F.Mask)
  (solder_mask_margin 0)
  (clearance 0)
  (solder_paste_margin 0)
  (solder_paste_ratio 0)
)''')

        p.clearance = 1.2
        p.solder_mask_margin = 2.3
        p.solder_paste_margin = 3.4
        p.solder_paste_ratio = 0.5
        self.assertSExpr(str(p), '''(pad 42 smd circle
  (at 1.5 2.6 42)
  (size 4 4)
  (layers F.Cu F.Paste F.Mask)
  (solder_mask_margin 2.3)
  (clearance 1.2)
  (solder_paste_margin 3.4)
  (solder_paste_ratio -25)
)''')

        p.thermal_width = 10
        p.thermal_gap = 20
        self.assertSExpr(str(p), '''(pad 42 smd circle
  (at 1.5 2.6 42)
  (size 4 4)
  (layers F.Cu F.Paste F.Mask)
  (solder_mask_margin 2.3)
  (clearance 1.2)
  (solder_paste_margin 3.4)
  (solder_paste_ratio -25)
  (zone_connect 1)
  (thermal_width 10)
  (thermal_gap 20)
)''')

    def testTestPad(self):
        p = fp.TestPad()
        self.assertSExpr(str(p), '''(pad 0 connect circle
  (at 0 0 0)
  (size 0 0)
  (layers F.Cu F.Mask)
  (solder_mask_margin 0)
  (clearance 0)
)''')

        p.name = 42
        p.shape = fp.PadShape.Obround
        self.assertSExpr(str(p), '''(pad 42 connect oval
  (at 0 0 0)
  (size 0 0)
  (layers F.Cu F.Mask)
  (solder_mask_margin 0)
  (clearance 0)
)''')

        p.center = (1.5, 2.6)
        p.angle = 42.2
        p.size = (10, 20)
        self.assertSExpr(str(p), '''(pad 42 connect oval
  (at 1.5 2.6 42.2)
  (size 10 20)
  (layers F.Cu F.Mask)
  (solder_mask_margin 0)
  (clearance 0)
)''')
        
        p.clearance = 1.1
        p.solder_mask_margin = 2.2
        self.assertSExpr(str(p), '''(pad 42 connect oval
  (at 1.5 2.6 42.2)
  (size 10 20)
  (layers F.Cu F.Mask)
  (solder_mask_margin 2.2)
  (clearance 1.1)
)''')

    def testConnector(self):
        p = fp.Connector()
        self.assertSExpr(str(p), '''(pad 0 connect circle
  (at 0 0 0)
  (size 0 0)
  (layers F.Cu F.Mask)
  (solder_mask_margin 0)
  (clearance 0)
)''')

    def testFootprint(self):
        f = fp.Footprint()
        self.assertSExpr(str(f), '''(module None
(layer F.Cu)
(tedit 0)
(at 0 0)
(descr "")
(fp_text reference "REF" (at 0 0) (layer F.SilkS) (effects (font (size 1 1) (thickness 0.15))))
(fp_text value "VAL" (at 0 0) (layer F.Fab) (effects (font (size 1 1) (thickness 0.15))))
)''')

        f.name = 'foo'
        f.description = 'A test footprint'
        self.assertSExpr(str(f), '''(module foo
(layer F.Cu)
(tedit 0)
(at 0 0)
(descr "A test footprint")
(fp_text reference "REF" (at 0 0) (layer F.SilkS) (effects (font (size 1 1) (thickness 0.15))))
(fp_text value "VAL" (at 0 0) (layer F.Fab) (effects (font (size 1 1) (thickness 0.15))))
)''')

        f.refdes.layer = fp.Layer.BottomSilkscreen
        f.value.hidden = True
        self.assertSExpr(str(f), '''(module foo
(layer F.Cu)
(tedit 0)
(at 0 0)
(descr "A test footprint")
(fp_text reference "REF" (at 0 0) (layer B.SilkS) (effects (font (size 1 1) (thickness 0.15))))
(fp_text value "VAL" (at 0 0) (layer F.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
)''')

        f.features.append(fp.Text(text='test feature'))
        self.assertSExpr(str(f), '''(module foo
(layer F.Cu)
(tedit 0)
(at 0 0)
(descr "A test footprint")
(fp_text reference "REF" (at 0 0) (layer B.SilkS) (effects (font (size 1 1) (thickness 0.15))))
(fp_text value "VAL" (at 0 0) (layer F.Fab) hide (effects (font (size 1 1) (thickness 0.15))))
(fp_text user "test feature" (at 0 0) (layer F.SilkS) (effects (font (size 1 1) (thickness 0.15))))
)''')
