from kidraw import footprint as fp
from kidraw import ipc
from kidraw.ipc import library as lib

def metric(s):
    return ("metric", s, lib.metric(s))

def imperial(s):
    return ("imperial", s, lib.imperial(s))

def test_point(size):
    f = fp.Footprint(name=f"Test Point {size}mm")
    f.features = [fp.TestPad(name=1, size=(size, size))]
    return f


def chip(size, polarized=False, profile=ipc.LandPatternSize.Nominal):
    t, n, s = size
    desc = "{0} ({1}) {2}chip device".format(n, t, "polarized " if polarized else "")
    f = fp.Footprint(name=n, description=desc)
    c = lib.chip(profile, s, polarized)
    f.from_ipc(c)
    return f


def SOIC(A, B, L, T, W, num_pins, pitch=1.27, profile=ipc.LandPatternSize.Nominal):
    f = fp.Footprint(name=f"{num_pins}-SOIC",
                     description=f"{num_pins}-pin SOIC")
    f.from_ipc(lib.SOIC(profile, A, B, L, T, W, num_pins, pitch))
    return f


def SOP(A, B, L, T, W, num_pins, pitch, profile=ipc.LandPatternSize.Nominal):
    f = fp.Footprint(name=f"{num_pins}-SOP",
                     description=f"{num_pins}-pin SOP")
    f.from_ipc(lib.SOP(profile, A, B, L, T, W, num_pins, pitch))
    return f


def SOT23(num_pins, profile=ipc.LandPatternSize.Nominal):
    f = fp.Footprint(name=f"SOT23-{num_pins}")
    f.from_ipc(lib.SOT23(profile, num_pins))
    return f


def SC70(num_pins, profile=ipc.LandPatternSize.Nominal):
    f = fp.Footprint(name=f"SC70-{num_pins}")
    f.from_ipc(lib.SC70(profile, num_pins))
    return f


def QFP(A, L, T, W, pitch, num_pins, profile=ipc.LandPatternSize.Nominal):
    f = fp.Footprint(name=f"{num_pins}-QFP",
                     description=f"{num_pins}-pin Quad Flat Package")
    f.from_ipc(lib.QFP(profile, A, L, T, W, pitch, num_pins))
    return f


def QFN(A, T, W, pitch, num_pins, profile=ipc.LandPatternSize.Nominal):
    f = fp.Footprint(name=f"{num_pins}-QFN",
                     description=f"{num_pins}-pin Quad Flat No-Leads")
    f.from_ipc(lib.QFN(profile, A, T, W, pitch, num_pins))
    return f
