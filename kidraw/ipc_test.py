import unittest

from kidraw import ipc

class TestDrawing(unittest.TestCase):
    """Trivial "code execution" tests for Drawing.*.

    This is really just testing for typos.
    """
    def testLayer(self):
        ls = [ipc.Drawing.Layer.Silkscreen,
              ipc.Drawing.Layer.Courtyard,
              ipc.Drawing.Layer.Assembly,
              ipc.Drawing.Layer.Documentation]

    def testFeatures(self):
        ipc.Drawing.Line(layer=1, points=2, width=3)
        ipc.Drawing.Circle(layer=1, center=2, radius=3)
        ipc.Drawing.Pad(number=1, center=2, size=3)

class TestDimension(unittest.TestCase):
    def testConstruct(self):
        d = ipc.Dimension(1, 2)
        self.assertEqual(d.min, 1)
        self.assertEqual(d.max, 2)
        self.assertEqual(d.nominal, 1.5)
        self.assertEqual(d.tolerance, 1)

    def testFromNominal(self):
        d1 = ipc.Dimension(1, 4)
        d2 = ipc.Dimension.from_nominal(2, plus=2, minus=1)
        self.assertEqual(d1.min, d2.min)
        self.assertEqual(d1.max, d2.max)
        self.assertEqual(d1.tolerance, d2.tolerance)
        # Nominal is not recorded, so d2.nominal is not the same value
        # we passed in.
        self.assertEqual(d2.nominal, 2.5)
        self.assertEqual(d1.nominal, d2.nominal)

class TestLandPatternSize(unittest.TestCase):
    # These tests don't check for exact values, since that would just
    # mean we duplicate the constants in multiple places, which is
    # silly.
    #
    # So, these tests cover basic execution (typos), checking that
    # constructors with parameters do vary based on the parameters,
    # and some *very* basic sanity checks on the resulting land
    # pattern data.

    def _makeLP(self, ctor, L, T, W, ctor_kwargs={}):
        """Checks that profiles become less strict as you'd expect, and that all construction is idempotent."""
        lpprev, Zprev, Gprev, Xprev = None, None, None, None
        for profile in (ipc.LandPatternSize.Least,
                        ipc.LandPatternSize.Nominal,
                        ipc.LandPatternSize.Most):
            lp = ctor(profile=profile, **ctor_kwargs)
            self.assertEqual(lp, ctor(profile=profile, **ctor_kwargs))
            Z = lp.OuterPadSpan(L, T)
            G = lp.InnerPadSpan(L, T)
            X = lp.PadWidth(W)
            if lpprev is not None:
                self.assertNotEqual(lp, lpprev)
                self.assertGreaterEqual(Z, Zprev)
                self.assertLessEqual(G, Gprev)
                self.assertGreaterEqual(X, Xprev)
            lpprev, Zprev, Gprev, Xprev = lp, Z, G, X
        return ctor(profile=ipc.LandPatternSize.Nominal, **ctor_kwargs)

    def testSimpleProfiles(self):
        L = ipc.Dimension.from_nominal(14, 0.1)
        T = ipc.Dimension.from_nominal(1, 0.1)
        W = ipc.Dimension.from_nominal(0.5, 0.1)

        for ctor in (ipc.LandPatternSize.J_leads,
                     ipc.LandPatternSize.inward_L_leads,
                     ipc.LandPatternSize.chip_array,
                     ipc.LandPatternSize.DIP_I_mount,
                     ipc.LandPatternSize.TO,
                     ipc.LandPatternSize.QFN,
                     ipc.LandPatternSize.SON,
                     ipc.LandPatternSize.MELF,
                     ipc.LandPatternSize.LCC,
                     ipc.LandPatternSize.SODFL,
                     ipc.LandPatternSize.SOTFL,
                     # aliases
                     ipc.LandPatternSize.PLCC,
                     ipc.LandPatternSize.SOJ,
                     ipc.LandPatternSize.concave_chip_array,
                     ipc.LandPatternSize.convex_chip_array,
                     ipc.LandPatternSize.flat_chip_array,
                     ipc.LandPatternSize.molded_capacitor,
                     ipc.LandPatternSize.molded_inductor,
                     ipc.LandPatternSize.molded_diode):
            lp = self._makeLP(ctor, L, T, W)
            # Pad should at least cover the nominal pin footprint.
            self.assertGreaterEqual(lp.OuterPadSpan(L, T), 14)
            self.assertLessEqual(lp.InnerPadSpan(L, T), 12)
            self.assertGreaterEqual(lp.PadWidth(W), 0.5)
                     
    def testGullwingLeads(self):
        A = ipc.Dimension.from_nominal(10, 0.1)
        L = ipc.Dimension.from_nominal(14, 0.1)
        T = ipc.Dimension.from_nominal(1, 0.1)
        W = ipc.Dimension.from_nominal(0.5, 0.1)

        for ctor in (ipc.LandPatternSize.gullwing_leads,
                     ipc.LandPatternSize.outward_L_leads,
                     ipc.LandPatternSize.SOIC,
                     ipc.LandPatternSize.SOP,
                     ipc.LandPatternSize.SOT,
                     ipc.LandPatternSize.SOD,
                     ipc.LandPatternSize.QFP,
                     ipc.LandPatternSize.CQFP,
                     ipc.LandPatternSize.LQFP,
                     ipc.LandPatternSize.TQFP):

            lp = self._makeLP(ipc.LandPatternSize.gullwing_leads,
                              L, T, W, {
                                  'A': A,
                                  'L': L,
                                  'T': T,
                                  'pitch': 1})

            # Pad should at least cover the nominal pin footprint.
            self.assertGreaterEqual(lp.OuterPadSpan(L, T), 14)
            self.assertLessEqual(lp.InnerPadSpan(L, T), 12)
            self.assertGreaterEqual(lp.PadWidth(W), 0.5)
        
            # Footprint whose pins sneak under the plastic package. Just
            # check that we get different constants, per the standard.
            L2 = ipc.Dimension.from_nominal(10, 0.1)
            lp2 = self._makeLP(ipc.LandPatternSize.gullwing_leads,
                               L2, T, W, {
                                   'A': A,
                                   'L': L2,
                                   'T': T,
                                   'pitch': 1})
            self.assertNotEqual(lp, lp2)

            # Fine-pitch footprint.
            lp2 = self._makeLP(ipc.LandPatternSize.gullwing_leads,
                               L, T, W, {
                                   'A': A,
                                   'L': L,
                                   'T': T,
                                   'pitch': 0.1})
            self.assertNotEqual(lp, lp2)

    def testChip(self):
        L = ipc.Dimension.from_nominal(14, 0.1)
        T = ipc.Dimension.from_nominal(1, 0.1)
        W = ipc.Dimension.from_nominal(0.5, 0.1)
        lp = self._makeLP(ipc.LandPatternSize.chip, L, T, W, {'L': L})

        # Pad should at least cover the nominal pin footprint.
        self.assertGreaterEqual(lp.OuterPadSpan(L, T), 14)
        self.assertLessEqual(lp.InnerPadSpan(L, T), 12)
        self.assertGreaterEqual(lp.PadWidth(W), 0.5)

        # Tiny components
        L = ipc.Dimension.from_nominal(1, 0.1)
        T = ipc.Dimension.from_nominal(0.2, 0.01)
        lp2 = self._makeLP(ipc.LandPatternSize.chip, L, T, W, {'L': L})
        self.assertNotEqual(lp, lp2)

    def testElectrolyticCapacitor(self):
        L = ipc.Dimension.from_nominal(14, 0.1)
        T = ipc.Dimension.from_nominal(1, 0.1)
        W = ipc.Dimension.from_nominal(0.5, 0.1)
        H = ipc.Dimension.from_nominal(5, 0.1)
        lp = self._makeLP(ipc.LandPatternSize.electrolytic_capacitor, L, T, W, {'H': H})

        # Pad should at least cover the nominal pin footprint.
        self.assertGreaterEqual(lp.OuterPadSpan(L, T), 14)
        self.assertLessEqual(lp.InnerPadSpan(L, T), 12)
        self.assertGreaterEqual(lp.PadWidth(W), 0.5)

        # Tall components
        H = ipc.Dimension.from_nominal(25, 0.1)
        lp2 = self._makeLP(ipc.LandPatternSize.electrolytic_capacitor, L, T, W, {'H': H})
        self.assertNotEqual(lp, lp2)

class TestDrawing(unittest.TestCase):
    def _drawing_as_string(self, d):
        ret = []
        for f in d.features:
            if isinstance(f, ipc.Drawing.Line):
                pts = ' '.join('({0:.2f} {1:.2f})'.format(x, y)
                               for x, y in f.points)
                ret.append('LINE {0} {1:.2f} {2}'.format(f.layer.name, f.width, pts))
            elif isinstance(f, ipc.Drawing.Circle):
                ret.append('CIRCLE {0} ({1[0]:.2f} {1[1]:.2f}) {2:.2f}'.format(f.layer.name, f.center, f.radius))
            elif isinstance(f, ipc.Drawing.Pad):
                ret.append('PAD {0} ({1[0]:.2f} {1[1]:.2f}) ({2[0]:.2f} {2[1]:.2f})'.format(f.number, f.center, f.size))
            else:
                raise ValueError('unexpected drawing feature type')
        return '\n'.join(sorted(ret))

    def _check_drawing(self, features, expected):
        self.maxDiff = None
        expected = '\n'.join(sorted(expected.strip().splitlines())).strip()
        self.assertMultiLineEqual(self._drawing_as_string(features), expected)
    
    def testTwoTerminalChip(self):
        # Chip-ish device
        A = ipc.Dimension.from_nominal(10, 0)
        B = ipc.Dimension.from_nominal(5, 0)
        L = ipc.Dimension.from_nominal(10, 0)
        T = ipc.Dimension.from_nominal(1, 0)
        W = ipc.Dimension.from_nominal(5, 0)
        spec = ipc.LandPatternSize(toe=0, heel=0, side=0, courtyard=0)

        expected = '''
PAD 1 (-4.50 0.00) (1.15 5.15)
PAD 2 (4.50 0.00) (1.15 5.15)

LINE Silkscreen 0.15 (-3.72 -2.57) (3.72 -2.57)
LINE Silkscreen 0.15 (-3.72 2.57) (3.72 2.57)

LINE Assembly 0.07 (-5.00 2.50) (-5.00 -2.50) (5.00 -2.50) (5.00 2.50) (-5.00 2.50)

LINE Documentation 0.15 (-1.96 0.00) (1.96 0.00)
LINE Documentation 0.15 (0.00 -1.96) (0.00 1.96)

LINE Courtyard 0.15 (-5.08 -2.65) (5.08 -2.65) (5.08 2.65) (-5.08 2.65) (-5.08 -2.65)
'''
        self._check_drawing(
            ipc.two_terminal_symmetric_device(
                A, B, L, T, W, spec, polarized=False), expected)

        expected = '''
PAD 1 (-4.50 0.00) (1.15 5.15)
PAD 2 (4.50 0.00) (1.15 5.15)

LINE Silkscreen 0.15 (-3.72 -2.57) (3.72 -2.57)
LINE Silkscreen 0.15 (-3.72 2.57) (-3.72 -2.57)
LINE Silkscreen 0.15 (-3.72 2.57) (3.72 2.57)
CIRCLE Silkscreen (-5.28 0.00) 0.10

LINE Assembly 0.07 (-5.00 2.50) (-5.00 -2.50) (5.00 -2.50) (5.00 2.50) (-5.00 2.50)

LINE Documentation 0.15 (-1.96 0.00) (1.96 0.00)
LINE Documentation 0.15 (0.00 -1.96) (0.00 1.96)

LINE Courtyard 0.15 (-5.38 -2.65) (5.08 -2.65) (5.08 2.65) (-5.38 2.65) (-5.38 -2.65)
'''
        self._check_drawing(
            ipc.two_terminal_symmetric_device(
                A, B, L, T, W, spec, polarized=True), expected)

    def testTwoTerminalMolded(self):
        # Molded-ish device
        A = ipc.Dimension.from_nominal(10, 0)
        B = ipc.Dimension.from_nominal(7, 0)
        L = ipc.Dimension.from_nominal(10, 0)
        T = ipc.Dimension.from_nominal(1, 0)
        W = ipc.Dimension.from_nominal(5, 0)
        spec = ipc.LandPatternSize(toe=0, heel=0, side=0, courtyard=0)

        expected = '''
PAD 1 (-4.50 0.00) (1.15 5.15)
PAD 2 (4.50 0.00) (1.15 5.15)

LINE Silkscreen 0.15 (-5.00 -2.77) (-5.00 -3.50)
LINE Silkscreen 0.15 (-5.00 -3.50) (5.00 -3.50)
LINE Silkscreen 0.15 (-5.00 2.77) (-5.00 3.50)
LINE Silkscreen 0.15 (-5.00 3.50) (5.00 3.50)
LINE Silkscreen 0.15 (5.00 -2.77) (5.00 -3.50)
LINE Silkscreen 0.15 (5.00 2.77) (5.00 3.50)

LINE Assembly 0.07 (-5.00 3.50) (-5.00 -3.50) (5.00 -3.50) (5.00 3.50) (-5.00 3.50)

LINE Documentation 0.15 (-1.96 0.00) (1.96 0.00)
LINE Documentation 0.15 (0.00 -1.96) (0.00 1.96)

LINE Courtyard 0.15 (-5.08 -3.58) (5.08 -3.58) (5.08 3.58) (-5.08 3.58) (-5.08 -3.58)
'''
        self._check_drawing(
            ipc.two_terminal_symmetric_device(
                A, B, L, T, W, spec, polarized=False), expected)

        expected = '''
PAD 1 (-4.50 0.00) (1.15 5.15)
PAD 2 (4.50 0.00) (1.15 5.15)

LINE Silkscreen 0.15 (-5.00 -2.77) (-5.00 -3.50)
LINE Silkscreen 0.15 (-5.00 -3.50) (5.00 -3.50)
LINE Silkscreen 0.15 (-5.00 2.77) (-5.00 3.50)
LINE Silkscreen 0.15 (-5.00 3.50) (5.00 3.50)
LINE Silkscreen 0.15 (5.00 -2.77) (5.00 -3.50)
LINE Silkscreen 0.15 (5.00 2.77) (5.00 3.50)
CIRCLE Silkscreen (-5.30 3.50) 0.10

LINE Assembly 0.07 (-5.00 3.50) (-5.00 -3.50) (5.00 -3.50) (5.00 3.50) (-5.00 3.50)

LINE Documentation 0.15 (-1.96 0.00) (1.96 0.00)
LINE Documentation 0.15 (0.00 -1.96) (0.00 1.96)

LINE Courtyard 0.15 (-5.40 -3.58) (5.08 -3.58) (5.08 3.60) (-5.40 3.60) (-5.40 -3.58)
'''
        self._check_drawing(
            ipc.two_terminal_symmetric_device(
                A, B, L, T, W, spec, polarized=True), expected)

    def testInLineTwoSide(self):
        A = ipc.Dimension.from_nominal(5, 0)
        B = ipc.Dimension.from_nominal(5, 0)
        LA = ipc.Dimension.from_nominal(7, 0)
        LB = ipc.Dimension.from_nominal(7, 0)
        T = ipc.Dimension.from_nominal(0.5, 0)
        W = ipc.Dimension.from_nominal(0.5, 0)
        pitch = 1
        spec = ipc.LandPatternSize(toe=0, heel=0, side=0, courtyard=0)

        expected = '''
PAD 1 (-3.25 1.50) (0.65 0.65)
PAD 2 (-3.25 0.50) (0.65 0.65)
PAD 3 (-3.25 -0.50) (0.65 0.65)
PAD 4 (-3.25 -1.50) (0.65 0.65)
PAD 5 (3.25 -1.50) (0.65 0.65)
PAD 6 (3.25 -0.50) (0.65 0.65)
PAD 7 (3.25 0.50) (0.65 0.65)
PAD 8 (3.25 1.50) (0.65 0.65)

LINE Silkscreen 0.15 (-2.50 -2.50) (2.50 -2.50)
LINE Silkscreen 0.15 (-2.50 2.50) (-2.50 -2.50)
LINE Silkscreen 0.15 (-2.50 2.50) (2.50 2.50)
LINE Silkscreen 0.15 (2.50 2.50) (2.50 -2.50)
CIRCLE Silkscreen (-3.88 1.50) 0.15

LINE Assembly 0.07 (-2.50 -0.25) (-3.00 -0.25) (-3.00 -0.75) (-2.50 -0.75)
LINE Assembly 0.07 (-2.50 -1.25) (-3.00 -1.25) (-3.00 -1.75) (-2.50 -1.75)
LINE Assembly 0.07 (-2.50 0.75) (-3.00 0.75) (-3.00 0.25) (-2.50 0.25)
LINE Assembly 0.07 (-2.50 1.75) (-3.00 1.75) (-3.00 1.25) (-2.50 1.25)
LINE Assembly 0.07 (-3.00 -0.25) (-3.50 -0.25) (-3.50 -0.75) (-3.00 -0.75) (-3.00 -0.25)
LINE Assembly 0.07 (-3.00 -1.25) (-3.50 -1.25) (-3.50 -1.75) (-3.00 -1.75) (-3.00 -1.25)
LINE Assembly 0.07 (-3.00 0.75) (-3.50 0.75) (-3.50 0.25) (-3.00 0.25) (-3.00 0.75)
LINE Assembly 0.07 (-3.00 1.75) (-3.50 1.75) (-3.50 1.25) (-3.00 1.25) (-3.00 1.75)
LINE Assembly 0.07 (2.50 -0.75) (3.00 -0.75) (3.00 -0.25) (2.50 -0.25)
LINE Assembly 0.07 (2.50 -1.75) (3.00 -1.75) (3.00 -1.25) (2.50 -1.25)
LINE Assembly 0.07 (2.50 0.25) (3.00 0.25) (3.00 0.75) (2.50 0.75)
LINE Assembly 0.07 (2.50 1.25) (3.00 1.25) (3.00 1.75) (2.50 1.75)
LINE Assembly 0.07 (2.50 2.50) (2.50 -2.50) (-2.50 -2.50) (-2.50 2.50) (2.50 2.50)
LINE Assembly 0.07 (3.00 -0.75) (3.50 -0.75) (3.50 -0.25) (3.00 -0.25) (3.00 -0.75)
LINE Assembly 0.07 (3.00 -1.75) (3.50 -1.75) (3.50 -1.25) (3.00 -1.25) (3.00 -1.75)
LINE Assembly 0.07 (3.00 0.25) (3.50 0.25) (3.50 0.75) (3.00 0.75) (3.00 0.25)
LINE Assembly 0.07 (3.00 1.25) (3.50 1.25) (3.50 1.75) (3.00 1.75) (3.00 1.25)

LINE Documentation 0.15 (0.00 0.62) (0.00 -0.62)
LINE Documentation 0.15 (0.62 0.00) (-0.62 0.00)

LINE Courtyard 0.15 (-4.03 -2.58) (3.58 -2.58) (3.58 2.58) (-4.03 2.58) (-4.03 -2.58)
'''
        self._check_drawing(
            ipc.in_line_pin_device(
                A, B, LA, LB, T, W, pitch, 4, 0, spec), expected)

        
        LA = ipc.Dimension.from_nominal(5, 0)
        expected = '''
PAD 1 (-2.25 1.50) (0.65 0.65)
PAD 2 (-2.25 0.50) (0.65 0.65)
PAD 3 (-2.25 -0.50) (0.65 0.65)
PAD 4 (-2.25 -1.50) (0.65 0.65)
PAD 5 (2.25 -1.50) (0.65 0.65)
PAD 6 (2.25 -0.50) (0.65 0.65)
PAD 7 (2.25 0.50) (0.65 0.65)
PAD 8 (2.25 1.50) (0.65 0.65)

LINE Silkscreen 0.15 (-2.50 -2.50) (-2.50 -2.15)
LINE Silkscreen 0.15 (-2.50 -2.50) (2.50 -2.50)
LINE Silkscreen 0.15 (-2.50 2.50) (-2.50 2.15)
LINE Silkscreen 0.15 (-2.50 2.50) (2.50 2.50)
LINE Silkscreen 0.15 (2.50 -2.50) (2.50 -2.15)
LINE Silkscreen 0.15 (2.50 2.50) (2.50 2.15)
CIRCLE Silkscreen (-2.87 1.50) 0.15

LINE Assembly 0.07 (-2.00 -0.25) (-2.50 -0.25) (-2.50 -0.75) (-2.00 -0.75) (-2.00 -0.25)
LINE Assembly 0.07 (-2.00 -1.25) (-2.50 -1.25) (-2.50 -1.75) (-2.00 -1.75) (-2.00 -1.25)
LINE Assembly 0.07 (-2.00 0.75) (-2.50 0.75) (-2.50 0.25) (-2.00 0.25) (-2.00 0.75)
LINE Assembly 0.07 (-2.00 1.75) (-2.50 1.75) (-2.50 1.25) (-2.00 1.25) (-2.00 1.75)
LINE Assembly 0.07 (2.00 -0.75) (2.50 -0.75) (2.50 -0.25) (2.00 -0.25) (2.00 -0.75)
LINE Assembly 0.07 (2.00 -1.75) (2.50 -1.75) (2.50 -1.25) (2.00 -1.25) (2.00 -1.75)
LINE Assembly 0.07 (2.00 0.25) (2.50 0.25) (2.50 0.75) (2.00 0.75) (2.00 0.25)
LINE Assembly 0.07 (2.00 1.25) (2.50 1.25) (2.50 1.75) (2.00 1.75) (2.00 1.25)
LINE Assembly 0.07 (2.50 2.50) (2.50 -2.50) (-2.50 -2.50) (-2.50 2.50) (2.50 2.50)

LINE Documentation 0.15 (0.00 0.62) (0.00 -0.62)
LINE Documentation 0.15 (0.62 0.00) (-0.62 0.00)

LINE Courtyard 0.15 (-3.02 -2.58) (2.58 -2.58) (2.58 2.58) (-3.02 2.58) (-3.02 -2.58)
'''
        self._check_drawing(
            ipc.in_line_pin_device(
                A, B, LA, LB, T, W, pitch, 4, 0, spec), expected)


    def testInLineFourSides(self):
        A = ipc.Dimension.from_nominal(5, 0)
        B = ipc.Dimension.from_nominal(5, 0)
        LA = ipc.Dimension.from_nominal(7, 0)
        LB = ipc.Dimension.from_nominal(7, 0)
        T = ipc.Dimension.from_nominal(0.5, 0)
        W = ipc.Dimension.from_nominal(0.5, 0)
        pitch = 1
        spec = ipc.LandPatternSize(toe=0, heel=0, side=0, courtyard=0)

        expected = '''
PAD 1 (-3.25 0.50) (0.65 0.65)
PAD 2 (-3.25 -0.50) (0.65 0.65)
PAD 3 (-0.50 -3.25) (0.65 0.65)
PAD 4 (0.50 -3.25) (0.65 0.65)
PAD 5 (3.25 -0.50) (0.65 0.65)
PAD 6 (3.25 0.50) (0.65 0.65)
PAD 7 (0.50 3.25) (0.65 0.65)
PAD 8 (-0.50 3.25) (0.65 0.65)

LINE Silkscreen 0.15 (-2.50 -2.50) (2.50 -2.50)
LINE Silkscreen 0.15 (-2.50 2.50) (-2.50 -2.50)
LINE Silkscreen 0.15 (-2.50 2.50) (2.50 2.50)
LINE Silkscreen 0.15 (2.50 2.50) (2.50 -2.50)
CIRCLE Silkscreen (-3.88 0.50) 0.15

LINE Assembly 0.07 (-0.25 2.50) (-0.25 3.00) (-0.75 3.00) (-0.75 2.50)
LINE Assembly 0.07 (-0.25 3.00) (-0.25 3.50) (-0.75 3.50) (-0.75 3.00) (-0.25 3.00)
LINE Assembly 0.07 (-0.75 -2.50) (-0.75 -3.00) (-0.25 -3.00) (-0.25 -2.50)
LINE Assembly 0.07 (-0.75 -3.00) (-0.75 -3.50) (-0.25 -3.50) (-0.25 -3.00) (-0.75 -3.00)
LINE Assembly 0.07 (-2.50 -0.25) (-3.00 -0.25) (-3.00 -0.75) (-2.50 -0.75)
LINE Assembly 0.07 (-2.50 0.75) (-3.00 0.75) (-3.00 0.25) (-2.50 0.25)
LINE Assembly 0.07 (-3.00 -0.25) (-3.50 -0.25) (-3.50 -0.75) (-3.00 -0.75) (-3.00 -0.25)
LINE Assembly 0.07 (-3.00 0.75) (-3.50 0.75) (-3.50 0.25) (-3.00 0.25) (-3.00 0.75)
LINE Assembly 0.07 (0.25 -2.50) (0.25 -3.00) (0.75 -3.00) (0.75 -2.50)
LINE Assembly 0.07 (0.25 -3.00) (0.25 -3.50) (0.75 -3.50) (0.75 -3.00) (0.25 -3.00)
LINE Assembly 0.07 (0.75 2.50) (0.75 3.00) (0.25 3.00) (0.25 2.50)
LINE Assembly 0.07 (0.75 3.00) (0.75 3.50) (0.25 3.50) (0.25 3.00) (0.75 3.00)
LINE Assembly 0.07 (2.50 -0.75) (3.00 -0.75) (3.00 -0.25) (2.50 -0.25)
LINE Assembly 0.07 (2.50 0.25) (3.00 0.25) (3.00 0.75) (2.50 0.75)
LINE Assembly 0.07 (2.50 2.50) (2.50 -2.50) (-2.50 -2.50) (-2.50 2.50) (2.50 2.50)
LINE Assembly 0.07 (3.00 -0.75) (3.50 -0.75) (3.50 -0.25) (3.00 -0.25) (3.00 -0.75)
LINE Assembly 0.07 (3.00 0.25) (3.50 0.25) (3.50 0.75) (3.00 0.75) (3.00 0.25)

LINE Documentation 0.15 (0.00 0.62) (0.00 -0.62)
LINE Documentation 0.15 (0.62 0.00) (-0.62 0.00)

LINE Courtyard 0.15 (-4.03 -3.58) (3.58 -3.58) (3.58 3.58) (-4.03 3.58) (-4.03 -3.58)
'''
        self._check_drawing(
            ipc.in_line_pin_device(
                A, B, LA, LB, T, W, pitch, 2, 2, spec), expected)

        LA = ipc.Dimension.from_nominal(5, 0)
        LB = ipc.Dimension.from_nominal(5, 0)
        expected = '''
PAD 1 (-2.25 0.50) (0.65 0.65)
PAD 2 (-2.25 -0.50) (0.65 0.65)
PAD 3 (-0.50 -2.25) (0.65 0.65)
PAD 4 (0.50 -2.25) (0.65 0.65)
PAD 5 (2.25 -0.50) (0.65 0.65)
PAD 6 (2.25 0.50) (0.65 0.65)
PAD 7 (0.50 2.25) (0.65 0.65)
PAD 8 (-0.50 2.25) (0.65 0.65)

LINE Silkscreen 0.15 (-2.50 -2.50) (-1.15 -2.50)
LINE Silkscreen 0.15 (-2.50 -2.50) (-2.50 -1.15)
LINE Silkscreen 0.15 (-2.50 2.50) (-1.15 2.50)
LINE Silkscreen 0.15 (-2.50 2.50) (-2.50 1.15)
LINE Silkscreen 0.15 (2.50 -2.50) (1.15 -2.50)
LINE Silkscreen 0.15 (2.50 -2.50) (2.50 -1.15)
LINE Silkscreen 0.15 (2.50 2.50) (1.15 2.50)
LINE Silkscreen 0.15 (2.50 2.50) (2.50 1.15)
CIRCLE Silkscreen (-2.87 0.50) 0.15

LINE Assembly 0.07 (-0.25 2.00) (-0.25 2.50) (-0.75 2.50) (-0.75 2.00) (-0.25 2.00)
LINE Assembly 0.07 (-0.75 -2.00) (-0.75 -2.50) (-0.25 -2.50) (-0.25 -2.00) (-0.75 -2.00)
LINE Assembly 0.07 (-2.00 -0.25) (-2.50 -0.25) (-2.50 -0.75) (-2.00 -0.75) (-2.00 -0.25)
LINE Assembly 0.07 (-2.00 0.75) (-2.50 0.75) (-2.50 0.25) (-2.00 0.25) (-2.00 0.75)
LINE Assembly 0.07 (0.25 -2.00) (0.25 -2.50) (0.75 -2.50) (0.75 -2.00) (0.25 -2.00)
LINE Assembly 0.07 (0.75 2.00) (0.75 2.50) (0.25 2.50) (0.25 2.00) (0.75 2.00)
LINE Assembly 0.07 (2.00 -0.75) (2.50 -0.75) (2.50 -0.25) (2.00 -0.25) (2.00 -0.75)
LINE Assembly 0.07 (2.00 0.25) (2.50 0.25) (2.50 0.75) (2.00 0.75) (2.00 0.25)
LINE Assembly 0.07 (2.50 2.50) (2.50 -2.50) (-2.50 -2.50) (-2.50 2.50) (2.50 2.50)

LINE Documentation 0.15 (0.00 0.62) (0.00 -0.62)
LINE Documentation 0.15 (0.62 0.00) (-0.62 0.00)

LINE Courtyard 0.15 (-3.02 -2.58) (2.58 -2.58) (2.58 2.58) (-3.02 2.58) (-3.02 -2.58)
'''
        self._check_drawing(
            ipc.in_line_pin_device(
                A, B, LA, LB, T, W, pitch, 2, 2, spec), expected)
