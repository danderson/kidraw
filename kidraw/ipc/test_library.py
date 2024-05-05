import os
import unittest

from kidraw import ipc
from kidraw.ipc import library as lib


class TestLibrary(unittest.TestCase):
    def _check_svg(self, name, fp):
        fp.scale(50)
        golden = os.path.join(
            os.path.dirname(__file__),
            "golden/%s.svg" % name)
        if os.environ.get("KIDRAW_WRITE_GOLDENS", False):
            with open(golden, "w") as f:
                f.write(fp.svg())
            return

        with open(golden) as f:
            golden = f.read()
        if fp.svg() != golden:
            (xmin, xmax), _ = fp.bounding_box
            out = [
                '<svg xmlns="http://www.w3.org/2000/svg" version="1.1">',
                fp.svg(),
                f'<g transform="translate({xmax - xmin + 20}, 0)">',
                golden,
                "</g>",
                "</svg>",
            ]
            diff = "diff.svg"
            with open(diff, "w") as f:
                f.write("\n".join(out))
            msg = """
Footprint {0} does not match golden.
Diff SVG written to {1} for inspection.
"""
            self.fail(msg.format(name, diff))

    PROFILES = {
        lib.Most: "M",
        lib.Nominal: "N",
        lib.Least: "L",
    }

    def testChips(self):
        for k in lib._chip_metric_dimensions.keys():
            for p, n in self.PROFILES.items():
                for polarized in (True, False):
                    name = "chip_m_%s_%s" % (k, n)
                    name += "P" if polarized else ""
                    fp = lib.chip(p, lib.metric(k), polarized)
                    self._check_svg(name, fp)
        for k in lib._chip_imperial_dimensions.keys():
            for p, n in self.PROFILES.items():
                for polarized in (True, False):
                    name = "chip_i_%s_%s" % (k, n)
                    name += "P" if polarized else ""
                    fp = lib.chip(p, lib.imperial(k), polarized)
                    self._check_svg(name, fp)

    def testSOIC(self):
        for p, n in self.PROFILES.items():
            name = "SOIC_%s" % n
            fp = lib.SOIC(p,
                          ipc.Dimension(3.8, 4),
                          ipc.Dimension(4.8, 5),
                          ipc.Dimension(5.8, 6.2),
                          ipc.Dimension(0.4, 1.27),
                          ipc.Dimension(0.3, 0.5),
                          8)
            self._check_svg(name, fp)

    def testSOP(self):
        for p, n in self.PROFILES.items():
            name = "TSSOP_%s" % n
            fp = lib.SOP(p,
                         ipc.Dimension(4.3, 4.5),
                         ipc.Dimension(2.9, 3.1),
                         ipc.Dimension(6.25, 6.5),
                         ipc.Dimension(0.5, 0.7),
                         ipc.Dimension(0.19, 0.3),
                         8,
                         0.65)
            self._check_svg(name, fp)

    def testSOT23_3(self):
        for p, n in self.PROFILES.items():
            name = "SOT23-3_%s" % n
            fp = lib.SOT23(p, 3)
            self._check_svg(name, fp)

    def testSOT23_5(self):
        for p, n in self.PROFILES.items():
            name = "SOT23-5_%s" % n
            fp = lib.SOT23(p, 5)
            self._check_svg(name, fp)

    def testSOT23_6(self):
        for p, n in self.PROFILES.items():
            name = "SOT23-6_%s" % n
            fp = lib.SOT23(p, 6)
            self._check_svg(name, fp)

    def testSOT23_8(self):
        for p, n in self.PROFILES.items():
            name = "SOT23-8_%s" % n
            fp = lib.SOT23(p, 8)
            self._check_svg(name, fp)

    def testSC70_5(self):
        for p, n in self.PROFILES.items():
            name = "SC70-5_%s" % n
            fp = lib.SC70(p, 5)
            self._check_svg(name, fp)

    def testSC70_6(self):
        for p, n in self.PROFILES.items():
            name = "SC70-6_%s" % n
            fp = lib.SC70(p, 6)
            self._check_svg(name, fp)

    def testSC70_8(self):
        for p, n in self.PROFILES.items():
            name = "SC70-8_%s" % n
            fp = lib.SC70(p, 8)
            self._check_svg(name, fp)

    def testQFP(self):
        for p, n in self.PROFILES.items():
            name = "QFP_%s" % n
            fp = lib.QFP(p,
                         ipc.Dimension(6.8, 7.2),
                         ipc.Dimension(8.8, 9.2),
                         ipc.Dimension(0.45, 0.75),
                         ipc.Dimension(0.3, 0.45),
                         0.8,
                         32)
            self._check_svg(name, fp)

    def testQFN(self):
        for p, n in self.PROFILES.items():
            name = "QFN_%s" % n
            fp = lib.QFN(p,
                         ipc.Dimension(4.9, 5.1),
                         ipc.Dimension(0.3, 0.5),
                         ipc.Dimension(0.18, 0.28),
                         0.5,
                         32)
            self._check_svg(name, fp)
