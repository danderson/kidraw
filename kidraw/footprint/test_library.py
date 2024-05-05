import os
import unittest

from kidraw import ipc
from kidraw.footprint import library as lib


class TestLibrary(unittest.TestCase):
    def _check_fp(self, name, fp):
        self.maxDiff = None
        golden = os.path.join(
            os.path.dirname(__file__),
            "golden/%s.kicad_mod" % name)
        if os.environ.get("KIDRAW_WRITE_GOLDENS", False):
            with open(golden, "w") as f:
                f.write(str(fp))
            return

        with open(golden) as f:
            golden = f.read()
        self.assertMultiLineEqual(str(fp), golden)

    def testChips(self):
        self._check_fp("0805", lib.chip(
            lib.imperial("0805")))
        self._check_fp("0805P", lib.chip(
            lib.imperial("0805"), polarized=True))
        self._check_fp("2012", lib.chip(
            lib.metric("2012")))
        self._check_fp("2012P", lib.chip(
            lib.metric("2012"), polarized=True))

    def testSOIC(self):
        self._check_fp("SOIC", lib.SOIC(
            ipc.Dimension(3.8, 4),
            ipc.Dimension(4.8, 5),
            ipc.Dimension(5.8, 6.2),
            ipc.Dimension(0.4, 1.27),
            ipc.Dimension(0.3, 0.5),
            8))

    def testSOP(self):
        self._check_fp("TSSOP", lib.SOP(
            ipc.Dimension(4.3, 4.5),
            ipc.Dimension(2.9, 3.1),
            ipc.Dimension(6.25, 6.5),
            ipc.Dimension(0.5, 0.7),
            ipc.Dimension(0.19, 0.3),
            8,
            0.65))

    def testSOT23(self):
        self._check_fp("SOT23-3", lib.SOT23(3))
        self._check_fp("SOT23-5", lib.SOT23(5))
        self._check_fp("SOT23-6", lib.SOT23(6))
        self._check_fp("SOT23-8", lib.SOT23(8))

    def testSC70(self):
        self._check_fp("SC70-5", lib.SC70(5))
        self._check_fp("SC70-6", lib.SC70(6))
        self._check_fp("SC70-8", lib.SC70(8))

    def testQFP(self):
        self._check_fp("QFP", lib.QFP(
                         ipc.Dimension(6.8, 7.2),
                         ipc.Dimension(8.8, 9.2),
                         ipc.Dimension(0.45, 0.75),
                         ipc.Dimension(0.3, 0.45),
                         0.8,
                         32))

    def testQFN(self):
        self._check_fp("QFN", lib.QFN(
                         ipc.Dimension(4.9, 5.1),
                         ipc.Dimension(0.3, 0.5),
                         ipc.Dimension(0.18, 0.28),
                         0.5,
                         32))
