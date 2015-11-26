#!/usr/bin/env python
"""Generates a bunch of sample footprints into an SVG.

This is mostly used during development, to sanity-check many
footprints one one shot.
"""

from kidraw import ipc

class Node(object):
    def __init__(self, x=0, y=0, w=800, h=None):
        self.x, self.y = x, y
        self.w, self.h = w, h
        self.drawing = None
        self.down = None
        self.right = None

    def __iter__(self):
        if self.drawing is not None:
            yield self.drawing, self.x, self.y
        if self.right is not None:
            for r in self.right:
                yield r
        if self.down is not None:
            for r in self.down:
                yield r
        
    def find_node(self, w, h):
        if self.drawing != None:
            d = self.down.find_node(w, h) if self.down != None else None
            r = self.right.find_node(w, h) if self.right != None else None
            return r or d
        if w > self.w:
            return None
        if self.h != None and h > self.h:
            return None
        return self

    def allocate(self, drawing, w, h):
        self.drawing = drawing
        self.down = Node(self.x,
                         self.y + h,
                         self.w,
                         self.h - h if self.h != None else None)
        self.right = Node(self.x + w,
                          self.y,
                          self.w - w,
                          h)

def binpack(drawings, w):
    def k(d):
        return -d[1].length * d[1].width
    drawings = sorted(drawings, key=k)
    t = Node(w=w)
    for n, d in drawings:
        w, h = d.length+10, d.width+30
        t.find_node(w, h).allocate((n, d), w, h)
    w, h = 0, 0
    for (_, d), x, y in t:
        w = max(w, x+d.length)
        h = max(h, y+d.width+30)
    out = [
        '<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{0}" height="{1}">'.format(w, h),
    ]
    out.append('<rect width="{0}" height="{1}" fill="black" />'.format(w, h))
    for (n, d), x, y in t:
        out.extend([
            '<g transform="translate({0}, {1})">'.format(x, y),
            d.svg(background_color="rgba(0, 0, 0, 0)"),
            '<text x="{0}" y="{1}" fill="green" stroke="green" text-anchor="middle" font-size="16">{2}</text>'.format(d.length/2, d.width+20, n),
            '</g>',
        ])
    out.append('</svg>')
    return '\n'.join(out)

def drawing(f):
    def run(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ipc.InfeasibleFootprint:
            r = ipc.Drawing()
            r.features += [
                ipc.Drawing.Line(
                    layer=ipc.Drawing.Layer.Documentation,
                    points=[(-1.5, -1.5), (1.5, 1.5)],
                    width=ipc.PenWidth),
                ipc.Drawing.Line(
                    layer=ipc.Drawing.Layer.Documentation,
                    points=[(-1.5, 1.5), (1.5, -1.5)],
                    width=ipc.PenWidth),
                ipc.Drawing.Line(
                    layer=ipc.Drawing.Layer.Courtyard,
                    points=[(-1.5, -1.5), (-1.5, 1.5), (1.5, 1.5), (1.5, -1.5), (-1.5, -1.5)],
                    width=ipc.PenWidth),
            ]
            return r
    return run

@drawing
def tqfp(profile):
    """STM32F042K6T6 microcontroller"""
    A = ipc.Dimension(6.8, 7.2)
    L = ipc.Dimension(8.8, 9.2)
    T = ipc.Dimension(0.450, 0.750)
    W = ipc.Dimension(0.3, 0.45)
    pitch = 0.8

    return ipc.in_line_pin_device(
        A, A, L, L, T, W, pitch, 8, 8,
        ipc.LandPatternSize.QFP(profile, A, L, T, pitch))

@drawing
def qfn(profile):
    """MAX3738 laser driver"""
    A = ipc.Dimension(3.9, 4.1)
    T = ipc.Dimension(0.3, 0.5)
    W = ipc.Dimension(0.18, 0.30)
    pitch = 0.5

    return ipc.in_line_pin_device(
        A=A, B=A, LA=A, LB=A, T=T, W=W, pitch=pitch,
        pins_leftright=6, pins_updown=6,
        spec=ipc.LandPatternSize.QFN(profile))

@drawing
def pqfn(profile):
    """QFN with pulled back leads"""
    A = ipc.Dimension(3.9, 4.1)
    L = ipc.Dimension(3.4, 3.6)
    T = ipc.Dimension(0.3, 0.5)
    W = ipc.Dimension(0.18, 0.30)
    pitch = 0.5

    return ipc.in_line_pin_device(
        A=A, B=A, LA=L, LB=L, T=T, W=W, pitch=pitch,
        pins_leftright=5, pins_updown=5,
        spec=ipc.LandPatternSize.QFN(profile))

@drawing
def dfn(profile):
    """PIC12F609"""
    A = ipc.Dimension.from_nominal(3, 0.1)
    T = ipc.Dimension(0.2, 0.55)
    W = ipc.Dimension(0.25, 0.35)
    pitch = 0.65

    return ipc.in_line_pin_device(
        A=A, B=A, LA=A, LB=A, T=T, W=W, pitch=pitch,
        pins_leftright=4, pins_updown=0,
        spec=ipc.LandPatternSize.DFN(profile))

@drawing
def soic(profile):
    """PIC12F609 microcontroller"""
    A = ipc.Dimension.from_nominal(3.9, 0.1)
    B = ipc.Dimension.from_nominal(4.9, 0.1)
    L = ipc.Dimension.from_nominal(6.0, 0.1)
    T = ipc.Dimension(0.4, 1.27)
    W = ipc.Dimension(0.31, 0.51)
    pitch = 1.27
    spec = ipc.LandPatternSize.SOIC(
        profile=profile,
        A=A, L=L, T=T, pitch=pitch)
    return ipc.in_line_pin_device(
        A=A, B=B, LA=L, LB=B, T=T, W=W, pitch=pitch,
        pins_leftright=4, pins_updown=0, spec=spec)

@drawing
def ssop(profile):
    """Some MAX-something transceiver"""
    A = ipc.Dimension(5.2, 5.38)
    B = ipc.Dimension(6.07, 6.33)
    L = ipc.Dimension(7.65, 7.90)
    T = ipc.Dimension(0.63, 0.95)
    W = ipc.Dimension(0.25, 0.38)
    pitch = 0.65

    spec = ipc.LandPatternSize.SOP(
        profile=profile,
        A=A, L=L, T=T, pitch=pitch)

    return ipc.in_line_pin_device(
        A=A, B=B, LA=L, LB=B, T=T, W=W, pitch=pitch,
        pins_leftright=8, pins_updown=0, spec=spec)

@drawing
def sc70(profile):
    """SCJW-8"""
    A = ipc.Dimension.from_nominal(1.75, 0.1)
    B = ipc.Dimension.from_nominal(2, 0.2)
    L = ipc.Dimension.from_nominal(2.1, 0.2)
    T = ipc.Dimension.from_nominal(0.45, 0.1)
    W = ipc.Dimension.from_nominal(0.225, 0.075)
    pitch = 0.5
    spec = ipc.LandPatternSize.SOJ(profile)
    return ipc.in_line_pin_device(
        A=A, B=B, LA=L, LB=B, T=T, W=W, pitch=pitch,
        pins_leftright=4, pins_updown=0, spec=spec)

@drawing
def tsopj(profile):
    """AAT1232 step-up converter"""
    A = ipc.Dimension.from_nominal(2.4, 0.1)
    B = ipc.Dimension.from_nominal(3, 0.1)
    L = ipc.Dimension.from_nominal(2.85, 0.2)
    T = ipc.Dimension.from_nominal(0.45, 0.15)
    W = ipc.Dimension.from_nominal(0.2, 0.1, 0.05)
    pitch = 0.5
    spec = ipc.LandPatternSize.SOJ(profile)
    return ipc.in_line_pin_device(
        A=A, B=B, LA=L, LB=B, T=T, W=W, pitch=pitch,
        pins_leftright=6, pins_updown=0, spec=spec)

@drawing
def chip(profile, size, polarized):
    if size == '0402':
        A = ipc.Dimension.from_nominal(1, 0.05)
        B = ipc.Dimension.from_nominal(0.5, 0.05)
        T = ipc.Dimension.from_nominal(0.2, 0.1)
    elif size == '0603':
        A = ipc.Dimension.from_nominal(1.55, 0.05)
        B = ipc.Dimension.from_nominal(0.85, 0.1)
        T = ipc.Dimension.from_nominal(0.3, 0.15, 0.2)
    elif size == '0805':
        A = ipc.Dimension.from_nominal(2, 0.1)
        B = ipc.Dimension.from_nominal(1.25, 0.15)
        T = ipc.Dimension.from_nominal(0.4, 0.1, 0.2)
    elif size == '1206':
        A = ipc.Dimension.from_nominal(3.2, 0.1, 0.2)
        B = ipc.Dimension.from_nominal(1.6, 0.15)
        T = ipc.Dimension.from_nominal(0.5, 0.25)
    else:
        raise ValueError('unknown chip spec')

    return ipc.two_terminal_symmetric_device(
        A=A, B=B, L=A, T=T, W=B,
        spec=ipc.LandPatternSize.chip(profile, A),
        polarized=polarized)

@drawing
def SOD(profile, polarized):
    A = ipc.Dimension(2.55, 2.85)
    B = ipc.Dimension(1.4, 1.7)
    L = ipc.Dimension(3.55, 3.85)
    T = ipc.Dimension(0.25, 0.4)
    W = ipc.Dimension.from_nominal(0.55, 0.1)
    return ipc.two_terminal_symmetric_device(
        A=A, B=B, L=L, T=T, W=W,
        spec=ipc.LandPatternSize.SOD(
            profile, A=A, L=L, T=T),
        polarized=polarized)

@drawing
def Molded(profile, polarized):
    A = ipc.Dimension.from_nominal(3.5, 0.2)
    B = ipc.Dimension.from_nominal(2.8, 0.2)
    T = ipc.Dimension.from_nominal(0.8, 0.3)
    W = ipc.Dimension.from_nominal(2.2, 0.1)
    return ipc.two_terminal_symmetric_device(
        A=A, B=B, L=A, T=T, W=W,
        spec=ipc.LandPatternSize.inward_L_leads(profile),
        polarized=polarized)

@drawing
def MELF(profile, polarized):
    A = ipc.Dimension(4.7, 5.2)
    B = ipc.Dimension(2.41, 2.67)
    T = ipc.Dimension(0.46, 0.56)
    return ipc.two_terminal_symmetric_device(
        A=A, B=B, L=A, T=T, W=B,
        spec=ipc.LandPatternSize.MELF(profile),
        polarized=polarized)

@drawing
def sot23_3(profile):
    A = ipc.Dimension(1.2, 1.4)
    B = ipc.Dimension(2.8, 3)
    L = ipc.Dimension(2.3, 2.5)
    T = ipc.Dimension(0.2, 0.3)
    W = ipc.Dimension(0.3, 0.51)
    pitch = 0.95
    return ipc.sot23_3(A=A, B=B, L=L, T=T, W=W, pitch=pitch,
                       spec=ipc.LandPatternSize.SOT(
                           profile, A, L, T, pitch))

@drawing
def sot23_5(profile):
    A = ipc.Dimension(1.5, 1.7)
    B = ipc.Dimension(2.8, 3)
    L = ipc.Dimension(2.6, 3)
    T = ipc.Dimension(0.35, 0.55)
    W = ipc.Dimension(0.35, 0.5)
    pitch = 0.95
    return ipc.sot23_5(A=A, B=B, L=L, T=T, W=W, pitch=pitch,
                       spec=ipc.LandPatternSize.SOT(
                           profile, A, L, T, pitch))

PROFILE = {
    ipc.LandPatternSize.Most: 'M',
    ipc.LandPatternSize.Nominal: 'N',
    ipc.LandPatternSize.Least: 'L',
}

fps = []
for p, l in PROFILE.items():
    fps.extend([
        ('32-TQFP-'+l, tqfp(p)),
        ('24-QFN-'+l, qfn(p)),
        ('20-PQFN-'+l, pqfn(p)),
        ('8-DFN-'+l, dfn(p)),
        ('8-SOIC-'+l, soic(p)),
        ('16-SSOP-'+l, ssop(p)),
        ('8-SC70-'+l, sc70(p)),
        ('12-TSOPJ-'+l, tsopj(p)),
        ('SOT23-3-'+l, sot23_3(p)),
        ('SOT23-5-'+l, sot23_5(p)),
    ])
    for polarized in (True, False):
        pol = 'P' if polarized else ''
        for size in ('0402', '0603', '0805', '1206'):
            fps.append(('%s-%s-%s' % (size, pol, l),
                        chip(p, size, polarized)))
        fps.append(('SOD-%s-%s' % (pol, l), SOD(p, polarized)))
        fps.append(('Molded-%s-%s' % (pol, l), Molded(p, polarized)))
        fps.append(('MELF-%s-%s' % (pol, l), MELF(p, polarized)))

print binpack([(n, x.scale(30)) for n, x in fps], w=1200)
