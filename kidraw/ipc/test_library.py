import os
import unittest
import webbrowser

from kidraw.ipc import library as lib

class TestLibrary(unittest.TestCase):
    def _check_svg(self, name, fp):
        fp.scale(50)
        golden = 'golden/%s.svg' % name
        if os.environ.get('KIDRAW_WRITE_GOLDENS', False):
            with open(golden, 'w') as f:
                f.write(fp.svg())
            return

        with open(golden) as f:
            golden = f.read()
        if fp.svg() != golden:
            (xmin, xmax), _ = fp.bounding_box
            out = [
                '<svg xmlns="http://www.w3.org/2000/svg" version="1.1">',
                fp.svg(),
                '<g transform="translate({0}, 0)">'.format(xmax-xmin+20),
                golden,
                '</g>',
                '</svg>',
            ]
            diff = 'diff.svg'
            with open(diff, 'w') as f:
                f.write('\n'.join(out))
            msg = '''
Footprint {0} does not match golden.
Diff SVG written to {1} for inspection.
'''
            self.fail(msg.format(name, diff))

    PROFILES = {
        lib.Most: 'M',
        lib.Nominal: 'N',
        lib.Least: 'L'
    }
            
    def testChips(self):
        for k in lib._chip_metric_dimensions.keys():
            for p, n in self.PROFILES.items():
                for polarized in (True, False):
                    name = 'metric'+k+n
                    name += 'P' if polarized else ''
                    fp = lib.chip(p, lib.metric(k), polarized)
                    self._check_svg(name, fp)
        for k in lib._chip_imperial_dimensions.keys():
            for p, n in self.PROFILES.items():
                for polarized in (True, False):
                    name = 'imperial'+k+n
                    name += 'P' if polarized else ''
                    fp = lib.chip(p, lib.imperial(k), polarized)
                    self._check_svg(name, fp)
