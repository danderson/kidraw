from kidraw import footprint as fp
from kidraw import ipc
from kidraw.ipc import library as lib

metric = lambda s: ('metric', s, lib.metric(s))
imperial = lambda s: ('imperial', s, lib.imperial(s))

def chip(size, polarized=False, profile=ipc.LandPatternSize.Nominal):
    t, n, s = size
    desc = '{0} ({1}) {2}chip device'.format(n, t, 'polarized ' if polarized else '')
    f = fp.Footprint(name=n, description=desc)
    c = lib.chip(profile, s, polarized)
    f.from_ipc(c)
    return f

def SOIC(A, B, L, T, W, num_pins, pitch=1.27, profile=ipc.LandPatternSize.Nominal):
    f = fp.Footprint(name='{0}-SOIC'.format(num_pins),
                     description='{0}-pin SOIC'.format(num_pins))
    f.from_ipc(lib.SOIC(profile, A, B, L, T, W, num_pins, pitch))
    return f

def SOP(A, B, L, T, W, num_pins, pitch, profile=ipc.LandPatternSize.Nominal):
    f = fp.Footprint(name='{0}-SOP'.format(num_pins),
                     description='{0}-pin SOP'.format(num_pins))
    f.from_ipc(lib.SOP(profile, A, B, L, T, W, num_pins, pitch))
    return f

def SOT23(num_pins, profile=ipc.LandPatternSize.Nominal):
    f = fp.Footprint(name='SOT23-{0}'.format(num_pins))
    f.from_ipc(lib.SOT23(profile, num_pins))
    return f

def SC70(num_pins, profile=ipc.LandPatternSize.Nominal):
    f = fp.Footprint(name='SC70-{0}'.format(num_pins))
    f.from_ipc(lib.SC70(profile, num_pins))
    return f

def QFP(A, L, T, W, pitch, num_pins, profile=ipc.LandPatternSize.Nominal):
    f = fp.Footprint(name='{0}-QFP'.format(num_pins),
                     description='{0}-pin Quad Flat Package'.format(num_pins))
    f.from_ipc(lib.QFP(profile, A, L, T, W, pitch, num_pins))
    return f

def QFN(A, T, W, pitch, num_pins, profile=ipc.LandPatternSize.Nominal):
    f = fp.Footprint(name='{0}-QFN'.format(num_pins),
                     description='{0}-pin Quad Flat No-Leads'.format(num_pins))
    f.from_ipc(lib.QFN(profile, A, T, W, pitch, num_pins))
    return f
