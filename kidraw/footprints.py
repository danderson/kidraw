import kidraw

# https://www.digikey.com/Web%20Export/Supplier%20Content/Vishay_8026/PDF/VishayBeyschlag_SolderPad.pdf
def _vishay_smd(d, name, w, pw, ph, polarized):
    x = (w - pw) / 2
    f = d.footprint(name)
    f.mask_margin(0.1)
    f.refdes().pos(0, ph)
    f.value().pos(0, -ph).fab()
    f.pad(1).smd().rect(pw, ph).pos(-x, 0)
    f.pad(2).smd().rect(pw, ph).pos(+x, 0)
    g = w/2 - 0.1
    x2 = ph/2 + 0.2
    f.line((-g, x2), (g, x2))
    f.line((-g, -x2), (g, -x2))
    if polarized:
        f.line((w/2 + 0.3, x2/1.5), (w/2 + 0.3, -x2/1.5))
    return f

def smd0603(d, polarized=False):
    return _vishay_smd(d, '0603', 2.9, 1.2, 1.1, polarized)

def smd0805(d, polarized=False):
    return _vishay_smd(d, '0805', 3.45, 1.4, 1.5, polarized)

def smd1206(d, polarized=False):
    return _vishay_smd(d, '1206', 4.7, 1.6, 1.9, polarized)

def sc70_6(d, name='SC70-6'):
    f = d.footprint(name)
    f.refdes().pos(0, 3)
    f.value()
    f.pad(1).smd().rect(0.47, 1).pos(-0.65,  0.9)
    f.pad(2).smd().rect(0.47, 1).pos( 0   ,  0.9)
    f.pad(3).smd().rect(0.47, 1).pos( 0.65,  0.9)
    f.pad(4).smd().rect(0.47, 1).pos( 0.65, -0.9)
    f.pad(5).smd().rect(0.47, 1).pos( 0   , -0.9)
    f.pad(6).smd().rect(0.47, 1).pos(-0.65, -0.9)
    f.line((-1.1, -0.675), ( 1.1, -0.675))
    f.line(( 1.1, -0.675), ( 1.1,  0.675))
    f.line(( 1.1,  0.675), (-1.1,  0.675))
    f.line((-1.1,  0.675), (-1.1, -0.675))
    f.circle((-1.185, 0.9), 0.1)
    return f

def sot323_6(d):
    return sc70_6(d, name='sot323_6')
