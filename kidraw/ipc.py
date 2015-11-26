from __future__ import division
from collections import namedtuple
from enum import Enum
import math

PenWidth = 0.15
AssemblyPenWidth = 0.1

class InfeasibleFootprint(Exception):
    pass

def two_terminal_symmetric_device(A, B, L, T, W, spec, polarized):
    """Returns drawing for a 2-terminal symmetric device.

    This is a generic footprint builder that will accept any
    LandPatternSize.

    If a polarized device is requested, pin 1 (the left-side pin) is
    the positive pin for capacitors, or the cathode for
    semiconductors.
    """
    Z, G = spec.OuterPadSpan(L, T), spec.InnerPadSpan(L, T)
    pad_width = spec.PadWidth(W)
    pad_length = (Z - G)/2
    pad_center_x = (G + pad_length)/2

    ret = Drawing()
    ret.features += [
        Drawing.Pad(number=1,
                    center=(-pad_center_x, 0),
                    size=(pad_length, pad_width)),
        Drawing.Pad(number=2,
                    center=(pad_center_x, 0),
                    size=(pad_length, pad_width)),

        # Origin mark
        Drawing.Line(layer=Drawing.Layer.Documentation,
                     points=[(-G/4, 0), (G/4, 0)],
                     width=PenWidth),
        Drawing.Line(layer=Drawing.Layer.Documentation,
                     points=[(0, -G/4), (0, G/4)],
                     width=PenWidth),

        # Assembly outline
        Drawing.Line(layer=Drawing.Layer.Assembly,
                     points=[(-A.nominal/2, B.nominal/2),
                             (-A.nominal/2, -B.nominal/2),
                             (A.nominal/2, -B.nominal/2),
                             (A.nominal/2, B.nominal/2),
                             (-A.nominal/2, B.nominal/2),
                     ],
                     width=AssemblyPenWidth),
    ]

    if L.nominal > A.nominal:
        ret.features += [
            Drawing.Line(layer=Drawing.Layer.Assembly,
                         points=[(-A.nominal/2, W.nominal/2),
                                 (-L.nominal/2, W.nominal/2),
                                 (-L.nominal/2, -W.nominal/2),
                                 (-A.nominal/2, -W.nominal/2),
                         ],
                         width=AssemblyPenWidth),
            Drawing.Line(layer=Drawing.Layer.Assembly,
                         points=[(A.nominal/2, W.nominal/2),
                                 (L.nominal/2, W.nominal/2),
                                 (L.nominal/2, -W.nominal/2),
                                 (A.nominal/2, -W.nominal/2),
                         ],
                         width=AssemblyPenWidth),
        ]

    if B.nominal > pad_width:
        # Silkscreen wraps around the pad side
        x, y = A.nominal/2, B.nominal/2
        ret.features += [
            Drawing.Line(layer=Drawing.Layer.Silkscreen,
                         points=[(-x, y), (x, y)],
                         width=PenWidth),
            Drawing.Line(layer=Drawing.Layer.Silkscreen,
                         points=[(-x, -y), (x, -y)],
                         width=PenWidth)
        ]
        v = pad_width/2 + 0.2
        if v < y:
            for xsign in (-1, 1):
                for ysign in (-1, 1):
                    ret.features.append(
                        Drawing.Line(layer=Drawing.Layer.Silkscreen,
                                     points=[(xsign*x, ysign*v), (xsign*x, ysign*y)],
                                     width=PenWidth))
        if polarized:
            ret.features.append(Drawing.Circle(
                layer=Drawing.Layer.Silkscreen,
                center=(-x-0.3, y),
                radius=0.1))
    else:
        # Silkscreen is within the pads.
        v = G/2 - 0.2
        ret.features += [
            Drawing.Line(layer=Drawing.Layer.Silkscreen,
                         points=[(-v, pad_width/2), (v, pad_width/2)],
                         width=PenWidth),
            Drawing.Line(layer=Drawing.Layer.Silkscreen,
                         points=[(-v, -pad_width/2), (v, -pad_width/2)],
                         width=PenWidth),
        ]
        if polarized:
            ret.features += [
                Drawing.Line(
                    layer=Drawing.Layer.Silkscreen,
                    points=[(-v, pad_width/2), (-v, -pad_width/2)],
                    width=PenWidth),
                Drawing.Circle(
                    layer=Drawing.Layer.Silkscreen,
                    center=(-Z/2-0.2, 0),
                    radius=0.1),
            ]

    _courtyard(ret, spec)
    return ret

def in_line_pin_device(A, B, LA, LB, T, W, pitch, pins_leftright, pins_updown, spec):
    """Returns drawing for a dual/quad in-line symmetric device.

    This is a generic footprint builder that will accept any
    LandPatternSize.
    """
    ret = Drawing()

    def pin_line(pad_center, pad_size, pin_tr, pin_size, pin_leg, offset, number, count):
        pad_center = list(pad_center)
        pin_tr = list(pin_tr)
        for n in range(number, number+count):
            ret.features.extend([
                Drawing.Pad(number=n,
                            center=tuple(pad_center),
                            size=pad_size,
                            obround=(n != 1)),
                Drawing.Line(layer=Drawing.Layer.Assembly,
                             points=[(pin_tr[0], pin_tr[1]),
                                     (pin_tr[0]+pin_size[0], pin_tr[1]),
                                     (pin_tr[0]+pin_size[0], pin_tr[1]+pin_size[1]),
                                     (pin_tr[0], pin_tr[1]+pin_size[1]),
                                     (pin_tr[0], pin_tr[1])],
                             width=AssemblyPenWidth),
            ])
            if pin_leg[0] != 0:
                ret.features.extend([
                    Drawing.Line(layer=Drawing.Layer.Assembly,
                                 points=[(pin_tr[0], pad_center[1]),
                                         (pin_tr[0]+pin_leg[0],
                                          pad_center[1])],
                                 width=AssemblyPenWidth),
                ])
            if pin_leg[1] != 0:
                ret.features.extend([
                    Drawing.Line(layer=Drawing.Layer.Assembly,
                                 points=[(pad_center[0], pin_tr[1]),
                                         (pad_center[0],
                                          pin_tr[1]+pin_leg[1])],
                                 width=AssemblyPenWidth),
                ])                
            pad_center[0] += offset[0]
            pad_center[1] += offset[1]
            pin_tr[0] += offset[0]
            pin_tr[1] += offset[1]

    Zlr, Glr = spec.OuterPadSpan(LA, T), spec.InnerPadSpan(LA, T)
    pad_lr_length = (Zlr - Glr)/2
    pad_lr_center = (Glr + pad_lr_length)/2

    Zud, Gud = spec.OuterPadSpan(LB, T), spec.InnerPadSpan(LB, T)
    pad_ud_length = (Zud - Gud)/2
    pad_ud_center = (Gud + pad_ud_length)/2

    pad_width = spec.PadWidth(W)
    if pitch - pad_width < 0.01:
        raise InfeasibleFootprint('Pad width is {0}, adjacent pins will short together (pitch {1})'.format(pad_width, pitch))
    
    pad_lr_y = (pins_leftright/2-0.5)*pitch
    pin_lr_tr = (LA.nominal/2 - T.nominal, pad_lr_y+W.nominal/2)
    pin_lr_size = (T.nominal, W.nominal)
    pin_lr_leg = (max(0, pin_lr_tr[0] - A.nominal/2), 0)

    pad_ud_x = (pins_updown/2-0.5)*pitch
    pin_ud_tl = (pad_lr_y+W.nominal/2, LB.nominal/2 - T.nominal)
    pin_ud_size = (W.nominal, T.nominal)
    pin_ud_leg = (0, max(0, pin_ud_tl[1] - B.nominal/2))

    pin_line((-pad_lr_center, pad_lr_y),
             (pad_lr_length, pad_width),
             (-pin_lr_tr[0], pin_lr_tr[1]),
             (-pin_lr_size[0], -pin_lr_size[1]),
             (pin_lr_leg[0], pin_lr_leg[1]),
             (0, -pitch),
             1,
             pins_leftright)
    pin_line((-pad_ud_x, -pad_ud_center),
             (pad_width, pad_ud_length),
             (-pin_ud_tl[0], -pin_ud_tl[1]),
             (pin_ud_size[0], -pin_ud_size[1]),
             (pin_ud_leg[0], pin_ud_leg[1]),
             (pitch, 0),
             pins_leftright+1,
             pins_updown)
    pin_line((pad_lr_center, -pad_lr_y),
             (pad_lr_length, pad_width),
             (pin_lr_tr[0], -pin_lr_tr[1]),
             (pin_lr_size[0], pin_lr_size[1]),
             (-pin_lr_leg[0], -pin_lr_leg[1]),
             (0, pitch),
             pins_leftright+pins_updown+1, pins_leftright)
    pin_line((pad_ud_x, pad_ud_center),
             (pad_width, pad_ud_length),
             (pin_ud_tl[0], pin_ud_tl[1]),
             (-pin_ud_size[0], pin_ud_size[1]),
             (-pin_ud_leg[0], -pin_ud_leg[1]),
             (-pitch, 0),
             pins_leftright+pins_updown+pins_leftright+1,
             pins_updown)

    x, y = A.nominal/2, B.nominal/2
    xstop, ystop = None, None
    if pins_leftright > 0 and x > (Glr/2 - PenWidth):
        # Pull the left/right lines back to just a notch at the top
        # and bottom.
        ystop = (pins_leftright/2-0.5)*pitch + pad_width/2 + PenWidth
        # If the pads are too close to the edge of the chip, pull the
        # silkscreen back away from the pad.
        if ystop > y:
            x = Glr/2 - PenWidth
            ystop = None
    if pins_updown > 0 and y > (Gud/2 - PenWidth):
        # Pull the top/bottom lines back to just a notch at the left
        # and right.
        xstop = (pins_updown/2-0.5)*pitch + pad_width/2 + PenWidth
        # If the pads are too close to the edge of the chip, pull the
        # silkscreen back away from the pad.
        if xstop > x:
            y = Gud/2 - PenWidth
            xstop = None

    if ystop is None:
        ret.features += [
            Drawing.Line(layer=Drawing.Layer.Silkscreen,
                         points=[(-x, y), (-x, -y)],
                         width=PenWidth),
            Drawing.Line(layer=Drawing.Layer.Silkscreen,
                         points=[(x, y), (x, -y)],
                         width=PenWidth),
        ]
    else:
        ret.features += [
            Drawing.Line(layer=Drawing.Layer.Silkscreen,
                         points=[(-x, y), (-x, ystop)],
                         width=PenWidth),
            Drawing.Line(layer=Drawing.Layer.Silkscreen,
                         points=[(-x, -y), (-x, -ystop)],
                         width=PenWidth),

            Drawing.Line(layer=Drawing.Layer.Silkscreen,
                         points=[(x, y), (x, ystop)],
                         width=PenWidth),
            Drawing.Line(layer=Drawing.Layer.Silkscreen,
                         points=[(x, -y), (x, -ystop)],
                         width=PenWidth),
        ]
        
    if xstop is None:
        ret.features += [
            Drawing.Line(layer=Drawing.Layer.Silkscreen,
                         points=[(-x, y), (x, y)],
                         width=PenWidth),
            Drawing.Line(layer=Drawing.Layer.Silkscreen,
                         points=[(-x, -y), (x, -y)],
                         width=PenWidth),
        ]
    else:
        ret.features += [
            Drawing.Line(layer=Drawing.Layer.Silkscreen,
                         points=[(-x, y), (-xstop, y)],
                         width=PenWidth),
            Drawing.Line(layer=Drawing.Layer.Silkscreen,
                         points=[(x, y), (xstop, y)],
                         width=PenWidth),

            Drawing.Line(layer=Drawing.Layer.Silkscreen,
                         points=[(-x, -y), (-xstop, -y)],
                         width=PenWidth),
            Drawing.Line(layer=Drawing.Layer.Silkscreen,
                         points=[(x, -y), (xstop, -y)],
                         width=PenWidth),
        ]

    ret.features += [
        Drawing.Line(
            layer=Drawing.Layer.Assembly,
            points=[(A.nominal/2, B.nominal/2),
                    (A.nominal/2, -B.nominal/2),
                    (-A.nominal/2, -B.nominal/2),
                    (-A.nominal/2, B.nominal/2),
                    (A.nominal/2, B.nominal/2)],
            width=AssemblyPenWidth),

        Drawing.Line(
            layer=Drawing.Layer.Documentation,
            points=[(pad_width/2, 0), (-pad_width/2, 0)],
            width=PenWidth),
        Drawing.Line(
            layer=Drawing.Layer.Documentation,
            points=[(0, pad_width/2), (0, -pad_width/2)],
            width=PenWidth),
    ]
    
    _courtyard(ret, spec)
    return ret

## Package classes.

def chip_device(profile, L, T, W, polarized):
    """Returns drawing for a chip device.

    Chip devices are rectangular packages named after their A and B
    dimensions, e.g. 0805, 0603, 2012... Chip packages are commonly
    used for resistors, capacitors, and LEDs.
    """
    lp = LandPatternSize.chip(profile, L.max)
    return two_terminal_symmetric_device(A=L, B=W, L=L, T=T, W=W, spec=lp, polarized=polarized)

def molded_body_device(profile, L, T, W, polarized):
    """Returns drawing for a molded body device.

    Molded body components have the electrical component encased in an
    epoxy resin, with L-lead terminations folding under the component.
    """
    lp = LandPatternSize.inward_L_leads(profile)
    return two_terminal_symmetric_device(A=L, B=W, L=L, T=T, W=W, spec=lp, polarized=polarized)

def melf_device(profile, L, T, W, polarized):
    """Returns drawing for a MELF (aka DO-213) body device."""
    lp = LandPatternSize.MELF(profile)
    return two_terminal_symmetric_device(A=L, B=W, L=L, T=T, W=W, spec=lp, polarized=polarized)

class Drawing(object):
    """Container for drawn footprint features."""

    def __init__(self):
        self.features = []

    @property
    def length(self):
        (xmin, xmax), _ = self.bounding_box
        return xmax-xmin

    @property
    def width(self):
        _, (ymin, ymax) = self.bounding_box
        return ymax-ymin

    @property
    def bounding_box(self):
        xmin, xmax = 0, 0
        ymin, ymax = 0, 0
        for f in self.features:
            if isinstance(f, Drawing.Line):
                for p in f.points:
                    xmin = min(xmin, p[0] - f.width/2)
                    xmax = max(xmax, p[0] + f.width/2)
                    ymin = min(ymin, p[1] - f.width/2)
                    ymax = max(ymax, p[1] + f.width/2)
            elif isinstance(f, Drawing.Circle):
                xmin = min(xmin, f.center[0] - f.radius)
                xmax = max(xmax, f.center[0] + f.radius)
                ymin = min(ymin, f.center[1] - f.radius)
                ymax = max(ymax, f.center[1] + f.radius)
            elif isinstance(f, Drawing.Pad):
                xmin = min(xmin, f.center[0] - f.size[0]/2)
                xmax = max(xmax, f.center[0] + f.size[0]/2)
                ymin = min(ymin, f.center[1] - f.size[1]/2)
                ymax = max(ymax, f.center[1] + f.size[1]/2)
            else:
                raise RuntimeError('Unexpected drawing feature type')
        return (xmin, xmax), (ymin, ymax)

    def scale(self, s):
        for f in self.features:
            if isinstance(f, Drawing.Line):
                f.points = [(x*s, y*s) for x,y in f.points]
                f.width *= s
            elif isinstance(f, Drawing.Circle):
                f.center = (f.center[0]*s, f.center[1]*s)
                f.radius *= s
            elif isinstance(f, Drawing.Pad):
                f.center = (f.center[0]*s, f.center[1]*s)
                f.size = (f.size[0]*s, f.size[1]*s)
        return self

    def svg(self, background_color='black', copper_color='red', silkscreen_color='white', assembly_color='yellow', documentation_color='blue', courtyard_color='magenta'):
        """Output an IPC footprint drawing as an SVG file.
        
        This is mostly for debugging and pretty pictures in
        documentation.
        """
        (xmin, xmax), (ymin, ymax) = self.bounding_box
        w, h = xmax-xmin, ymax-ymin
        out = [
            '<svg xmlns="http://www.w3.org/2000/svg" version="1.1">',
            '<g transform="translate({0}, {1})">'.format(-xmin, -ymin),
            '<rect x="{0}" y="{1}" width="{2}" height="{3}" fill="{4}" />'.format(
                -w/2, -h/2, w, h, background_color),
        ]
        colormap = {
            Drawing.Layer.Silkscreen: silkscreen_color,
            Drawing.Layer.Assembly: assembly_color,
            Drawing.Layer.Documentation: documentation_color,
            Drawing.Layer.Courtyard: courtyard_color,
        }
        for f in self.features:
            if isinstance(f, Drawing.Line):
                pts = ['{0},{1}'.format(x, -y) for x, y in f.points]
                opacity = 1 if f.layer == Drawing.Layer.Silkscreen else 0.6
                out.append(
                    '<polyline points="{0}" stroke="{1}" stroke-width="{2}" opacity="{3}" fill="none" stroke-linecap="round" />'.format(
                        ' '.join(pts), colormap[f.layer], f.width, opacity))
            elif isinstance(f, Drawing.Circle):
                out.append(
                    '<circle cx="{0}" cy="{1}" r="{2}" fill="{3}" opacity="0.8" />'.format(
                        f.center[0], -f.center[1], f.radius, colormap[f.layer]))
            elif isinstance(f, Drawing.Pad):
                out.append(
                    '<rect x="{0}" y="{1}" width="{2}" height="{3}" rx="{4}" ry="{4}" fill="{5}" opacity="0.8" />'.format(
                        f.center[0]-f.size[0]/2, -(f.center[1]+f.size[1]/2),
                        f.size[0], f.size[1],
                        min(f.size[0], f.size[1])/2 if f.obround else 0,
                        copper_color))
            else:
                raise RuntimeError('Unknown drawing feature type')
        out += [
            '</g>',
            '</svg>',
        ]
        return '\n'.join(out)

    Layer = Enum(
        'Layer', ['Silkscreen', 'Courtyard', 'Assembly', 'Documentation'])

    class Line(object):
        def __init__(self, layer, points, width):
            self.layer = layer
            self.points = points
            self.width = width

    class Circle(object):
        def __init__(self, layer, center, radius):
            self.layer = layer
            self.center = center
            self.radius = radius

    class Pad(object):
        def __init__(self, number, center, size, obround=False):
            self.number = number
            self.center = center
            self.size = size
            # Drawing suggestion: obround shape preferred if True,
            # else square.
            self.obround = obround
    
class Dimension(object):
    """Records a dimension with tolerances."""
    def __init__(self, min, max):
        """Construct a Dimension given min and max values."""
        assert min <= max
        self.min, self.max = min, max

    @classmethod
    def from_nominal(cls, nominal, plus, minus=None):
        """Construct a Dimension given nominal and plus/minus values."""
        if minus is None:
            minus = plus
        return cls(nominal-minus, nominal+plus)

    @property
    def tolerance(self):
        """The tolerance is the min-max delta of the Dimension."""
        return self.max - self.min

    @property
    def nominal(self):
        """The nominal value of the Dimension, assuming equal plus and minus tolerance."""
        return self.min + (self.tolerance/2)

class LandPatternSize(object):
    """Empirically-defined constants for pad and courtyard oversizing.

    IPC-7351B specifies, for each class of component footprint
    (i.e. the way they contact the PCB), how much larger or smaller
    the pad should be than the pin.

    Additionally, it specifies a per-class "courtyard excess",
    additional margin that should be added to the combined bounding
    box of the component and its land pattern.
    """

    # These are the protrusion profiles defined by the Standard.
    Most = 0
    Nominal = 1
    Least = 2

    def __init__(self, toe, heel, side, courtyard, rounding_increment=0.05):
        self.toe = toe
        self.heel = heel
        self.side = side
        self.courtyard = courtyard
        self.rounding_increment = rounding_increment
        # PCB tolerance is how (im)precisely the PCB manufacturer can
        # etch to the exact dimensions we give them.
        self.pcb_tolerance = 0.1
        # Place tolerance is how (im)precisely the pick-and-place
        # machine can place components at the design position.
        self.place_tolerance = 0.05

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
        
    def _round_down(self, x):
        return round(x - (x % self.rounding_increment), 2)

    def _round_up(self, x):
        return self._round_down(x) + self.rounding_increment

    def OuterPadSpan(self, L, T):
        """Returns the outer pad span.

        The outer pad span is the distance from the leftmost edge of
        the left-side pad column, to the rightmost edge of the
        right-side pad column.

        This calculation assumes that the pad lengths on either side
        of the component are identical. Asymmetric components like
        SOT223 or TO252 will need to do additional work to calculate
        the pad dimensions for each side separately.

        This dimension is called Z_max in the standard.
        """
        # The standard calls this dimension Z(max).
        return self._round_up(L.min + 2*self.toe + _rms(L.tolerance, self.pcb_tolerance, self.place_tolerance))

    def InnerPadSpan(self, L, T):
        """Returns the inner pad span.

        The inner pad span is the distance from the rightmost edge of
        the left-side pad column, to the leftmost edge of the
        right-side pad column.

        This calculation assumes that the pad lengths on either side
        of the component are identical. Asymmetric components like
        SOT223 or TO252 will need to do additional work to calculate
        the pad dimensions for each side separately.

        This dimension is called G_min in the standard.
        """
        # Calculate S, the inner pin-to-pin dimension.
        rms = _rms(L.tolerance, T.tolerance)
        S = Dimension(L.min - 2*T.max + rms/2,
                      L.max - 2*T.min - rms/2)
        # and use it to calculate G(min).
        Gmin = self._round_down(S.max - 2*self.heel - _rms(S.tolerance, self.pcb_tolerance, self.place_tolerance))
        if Gmin <= 0:
            raise InfeasibleFootprint('Inner pad span is {0}, pads will short together'.format(Gmin))
        return Gmin
    
    def PadWidth(self, W):
        """Returns the pad width given component pin width.

        This dimension is called X_max in the standard.
        """
        return self._round_up(W.min + 2*self.side + _rms(W.tolerance, self.pcb_tolerance, self.place_tolerance))

    #
    # Constructors for component archetypes begins here.
    #
    
    @classmethod
    def gullwing_leads(cls, profile, A, L, T, pitch=None):
        """Gull wing or outward-facing L leads.

        This profile notably covers ICs in the SOIC, SOP, SOT, SOD and
        QFP families.
        """
        toe = [0.55, 0.35, 0.15]
        heel = [0.45, 0.35, 0.25]
        side = [0.05, 0.03, 0.01]
        courtyard = [0.5, 0.25, 0.1]
        Smin = L.min - 2*T.max
        if Smin <= A.max:
            heel = [0.25, 0.15, 0.05]
        if pitch is not None and pitch <= 0.625:
            side = [0.01, -0.02, -0.04]
        return cls(toe[profile], heel[profile], side[profile], courtyard[profile])

    @classmethod
    def J_leads(cls, profile):
        """J leads, bending back under the component.

        This profile notably covers ICs in the PLCC and SOJ families.
        """
        # Note: because J-leads bend backwards, the heel is used to
        # calculate the outer pattern dimension, and the toe for the
        # inner dimension. Thus, what we pass as the "toe" argument to
        # the constructor is technically actually the heel fillet, and
        # the "heel" argument is the toe fillet.
        return cls([0.55, 0.35, 0.15][profile],
                   [0.10, 0.00, -0.10][profile],
                   [0.05, 0.03, 0.01][profile],
                   [0.5, 0.25, 0.1][profile])

    outward_L_leads = gullwing_leads

    @classmethod
    def inward_L_leads(cls, profile):
        """L leads, bending back under the component.

        This profile notably covers the "molded body" family of
        capacitors, inductors and diodes - for example Vishay's TR3
        series of tantalum capacitors.
        """

        # Like the J leads, heel and toe dimensions are flipped.
        return cls([0.25, 0.15, 0.07][profile],
                   [0.8, 0.5, 0.2][profile],
                   [0.01, -0.05, -0.10][profile],
                   [0.5, 0.25, 0.1][profile])

    @classmethod
    def chip(cls, profile, L):
        """2-terminal chip components.

        This profile notably covers devices whose packages are named
        after their physical dimensions: 0603, 2012 (0805 imperial),
        and so forth.
        """
        toe = [0.55, 0.35, 0.15]
        side = [0.05, 0, -0.05]
        courtyard = [0.5, 0.25, 0.1]
        rounding_increment = 0.5
        if L.max < 1.6:
            toe = [0.3, 0.2, 0.1]
            courtyard = [0.2, 0.15, 0.1]
            # Small chip components is the only place where rounding
            # is specified to an increment other than 0.5.
            rounding_increment = 0.2
        return cls(toe[profile], 0, side[profile], courtyard[profile], rounding_increment)

    @classmethod
    def chip_array(cls, profile):
        """Leadless terminal arrays.

        This specifically covers arrays of passives that come in
        "Concave Chip Array", "Convex Chip Array", or "Flat Chip
        Array" packages.
        """
        return cls([0.55, 0.45, 0.35][profile],
                   [-0.05, -0.07, -0.10][profile],
                   [-0.05, -0.07, -0.10][profile],
                   [0.5, 0.25, 0.1][profile])

    @classmethod
    def electrolytic_capacitor(cls, profile, H):
        """Electrolytic SMD capacitor on a notched rectangular base.

        This covers a single package type that most SMD electrolytics
        come as. For example, the Vishay 140 CRH family uses this
        package.
        """
        toe = [0.7, 0.5, 0.3]
        heel = [0, -0.1, -0.2]
        side = [0.5, 0.4, 0.3]
        if H.max > 10:
            toe = [1.0, 0.7, 0.4]
            heel = [0, -0.05, -0.10]
            side = [0.6, 0.5, 0.4]
        return cls(toe[profile],
                   heel[profile],
                   side[profile],
                   [1.0, 0.5, 0.25][profile])

    @classmethod
    def DIP_I_mount(cls, profile):
        """Butt-mounted DIP packages.

        The Standard specifies a technique for surface-mounting DIP
        packages: cut the leads flush with the bottom of the DIP body,
        and solder the remaining vertical lead to a large SMD pad.

        This is very esoteric, but a very small number of components
        come direct from the factory in "DIP butt joint" packaging,
        with the DIP leads pre-cut.
        """
        return cls([1.0, 0.8, 0.6][profile],
                   [1.0, 0.8, 0.6][profile],
                   [0.3, 0.2, 0.1][profile],
                   [1.5, 0.8, 0.2][profile])

    @classmethod
    def TO(cls, profile):
        """Surface-mount DPAK/TO type package."""
        return cls([0.55, 0.35, 0.15][profile],
                   [0.45, 0.35, 0.25][profile],
                   [0.05, 0.03, 0.01][profile],
                   [0.5, 0.25, 0.1][profile])

    @classmethod
    def QFN(cls, profile):
        """Leadless IC packages with pads only on the bottom.

        This covers all QFN and SON packages.
        """
        return cls([0.4, 0.3, 0.2][profile],
                   0,
                   -0.04,
                   [0.5, 0.25, 0.1][profile])

    @classmethod
    def MELF(cls, profile):
        """MELF/DO-213 package."""
        return cls([0.6, 0.4, 0.2][profile],
                   [0.2, 0.1, 0.02][profile],
                   [0.1, 0.05, 0.01][profile],
                   [0.5, 0.25, 0.1][profile])

    @classmethod
    def LCC(cls, profile):
        """LCC package.

        Careful, this is not PLCC! LCC packages are leadless and a
        closer relative of QFN.
        """
        # Like j_leads, heel and toe are swapped here.
        return cls([0.65, 0.55, 0.45][profile],
                   [0.25, 0.15, 0.05][profile],
                   [0.05, -0.05, -0.15][profile],
                   [0.5, 0.25, 0.1][profile])

    @classmethod
    def SODFL(cls, profile):
        """Small outline flat lead diode/transistor."""
        return cls([0.3, 0.2, 0.1][profile],
                   0,
                   [0.05, 0, -0.05][profile],
                   [0.2, 0.15, 0.1][profile])
    SOTFL = SODFL

    # Finally, constructor aliases for the generic classes, so that
    # you don't need to go figure out whether a SOIC is a J-lead,
    # Gullwing, flag, leadless, or whatever package.
    SOIC = gullwing_leads
    SOP = gullwing_leads
    SOT = gullwing_leads
    SOD = gullwing_leads
    QFP = gullwing_leads
    CQFP = gullwing_leads
    LQFP = gullwing_leads
    TQFP = gullwing_leads
    
    PLCC = J_leads
    SOJ = J_leads

    DFN = QFN
    SON = QFN
    
    chip_resistor = chip
    chip_capacitor = chip
    chip_inductor = chip
    chip_diode = chip

    concave_chip_array = chip_array
    convex_chip_array = chip_array
    flat_chip_array = chip_array

    molded_capacitor = inward_L_leads
    molded_inductor = inward_L_leads
    molded_diode = inward_L_leads

def _printret(x):
    """Debugging helper"""
    print x
    return x
    
def _rms(*args):
    return math.sqrt(sum(x**2 for x in args))

def _courtyard(drawing, spec):
    (xmin, xmax), (ymin, ymax) = drawing.bounding_box
    xmin -= spec.courtyard
    xmax += spec.courtyard
    ymin -= spec.courtyard
    ymax += spec.courtyard

    drawing.features.append(
        Drawing.Line(layer=Drawing.Layer.Courtyard,
                     points=[(xmin, ymin),
                             (xmax, ymin),
                             (xmax, ymax),
                             (xmin, ymax),
                             (xmin, ymin)],
                     width=PenWidth))
