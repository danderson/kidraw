"""Reference IPC7351 land patterns.

This library provides reference footprints for common parts like chip
resistors, for designs that just need a "generic 0805" land pattern
that will probably work.
"""

import sys
from kidraw import ipc

Most = ipc.LandPatternSize.Most
Nominal = ipc.LandPatternSize.Nominal
Least = ipc.LandPatternSize.Least

def _chip(profile, polarized, A, B, T):
    spec = ipc.LandPatternSize.chip(profile, A)
    return ipc.two_terminal_symmetric_device(
        A, B, A, T, B, spec, polarized)

_CHIP_DIMENSIONS = {
    '1005': (ipc.Dimension.from_nominal(1.00, 0.05),
             ipc.Dimension.from_nominal(0.50, 0.05),
             ipc.Dimension.from_nominal(0.2, 0.10)),
    '1608': (ipc.Dimension.from_nominal(1.55, 0.05),
             ipc.Dimension.from_nominal(0.85, 0.10),
             ipc.Dimension.from_nominal(0.3, 0.15, 0.20)),
    '2012': (ipc.Dimension.from_nominal(2.00, 0.10),
             ipc.Dimension.from_nominal(1.25, 0.15),
             ipc.Dimension.from_nominal(0.4, 0.1, 0.2)),
    '3216': (ipc.Dimension.from_nominal(3.20, 0.1, 0.2),
             ipc.Dimension.from_nominal(1.60, 0.15),
             ipc.Dimension.from_nominal(0.50, 0.25)),
}

_CHIP_IMPERIAL = {
    '0402': '1005',
    '0603': '1608',
    '0805': '2012',
    '1206': '3216',
}

_current_module = sys.modules[__name__]
_metric_to_imperial = dict((v, k) for k, v in _CHIP_IMPERIAL.items())
for n, dims in _CHIP_DIMENSIONS.items():
    mname = 'metric'+n
    iname = 'imperial'+_metric_to_imperial[n]
    x, y, z = dims
    def f(dims):
        def r(profile, polarized):
            return _chip(profile, polarized, *dims)
        return r
    f.__doc__ = 'Footprint for a {0} ({1} imperial) chip device'.format(n, _metric_to_imperial[n])
    setattr(_current_module, mname, f(dims))
    setattr(_current_module, iname, f(dims))
