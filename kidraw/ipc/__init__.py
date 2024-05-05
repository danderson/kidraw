"""Compute SMD land pattern dimensions based on IPC-7351B.

This module is deliberately decoupled from kidraw's drawing routines,
so that the output of the math can be reused by other projects if
desired.
"""
import math
from enum import Enum

PenWidth = 0.15
AssemblyPenWidth = 0.075


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
    pad_length = (Z - G) / 2
    pad_center_x = (G + pad_length) / 2

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
                     points=[(-G / 4, 0), (G / 4, 0)],
                     width=PenWidth),
        Drawing.Line(layer=Drawing.Layer.Documentation,
                     points=[(0, -G / 4), (0, G / 4)],
                     width=PenWidth),

        # Assembly outline
        Drawing.Line(layer=Drawing.Layer.Assembly,
                     points=[(-A.nominal / 2, B.nominal / 2),
                             (-A.nominal / 2, -B.nominal / 2),
                             (A.nominal / 2, -B.nominal / 2),
                             (A.nominal / 2, B.nominal / 2),
                             (-A.nominal / 2, B.nominal / 2),
                     ],
                     width=AssemblyPenWidth),
    ]

    if L.nominal > A.nominal:
        ret.features += [
            Drawing.Line(layer=Drawing.Layer.Assembly,
                         points=[(-A.nominal / 2, W.nominal / 2),
                                 (-L.nominal / 2, W.nominal / 2),
                                 (-L.nominal / 2, -W.nominal / 2),
                                 (-A.nominal / 2, -W.nominal / 2),
                         ],
                         width=AssemblyPenWidth),
            Drawing.Line(layer=Drawing.Layer.Assembly,
                         points=[(A.nominal / 2, W.nominal / 2),
                                 (L.nominal / 2, W.nominal / 2),
                                 (L.nominal / 2, -W.nominal / 2),
                                 (A.nominal / 2, -W.nominal / 2),
                         ],
                         width=AssemblyPenWidth),
        ]

    if B.nominal > pad_width:
        # Silkscreen wraps around the pad side
        x, y = A.nominal / 2, B.nominal / 2
        ret.features += [
            Drawing.Line(layer=Drawing.Layer.Silkscreen,
                         points=[(-x, y), (x, y)],
                         width=PenWidth),
            Drawing.Line(layer=Drawing.Layer.Silkscreen,
                         points=[(-x, -y), (x, -y)],
                         width=PenWidth),
        ]
        v = pad_width / 2 + 0.2
        if v < y:
            for xsign in (-1, 1):
                for ysign in (-1, 1):
                    ret.features.append(
                        Drawing.Line(layer=Drawing.Layer.Silkscreen,
                                     points=[(xsign * x, ysign * v), (xsign * x, ysign * y)],
                                     width=PenWidth))
        if polarized:
            ret.features.append(Drawing.Circle(
                layer=Drawing.Layer.Silkscreen,
                center=(-x - 0.3, y),
                radius=0.1))
    else:
        # Silkscreen is within the pads.
        v = G / 2 - 0.2
        ret.features += [
            Drawing.Line(layer=Drawing.Layer.Silkscreen,
                         points=[(-v, pad_width / 2), (v, pad_width / 2)],
                         width=PenWidth),
            Drawing.Line(layer=Drawing.Layer.Silkscreen,
                         points=[(-v, -pad_width / 2), (v, -pad_width / 2)],
                         width=PenWidth),
        ]
        if polarized:
            ret.features += [
                Drawing.Line(
                    layer=Drawing.Layer.Silkscreen,
                    points=[(-v, pad_width / 2), (-v, -pad_width / 2)],
                    width=PenWidth),
                Drawing.Circle(
                    layer=Drawing.Layer.Silkscreen,
                    center=(-Z / 2 - 0.2, 0),
                    radius=0.1),
            ]

    _courtyard(ret, spec)
    return ret


def _pin_line(ret, spec, A, L, T, W, pitch, start_pin, num_pins, rotation):
    Z, G = spec.OuterPadSpan(L, T), spec.InnerPadSpan(L, T)
    pad_width = spec.PadWidth(W)
    if pitch - pad_width < spec.pcb_tolerance:
        raise InfeasibleFootprint(f"Pad width {pad_width} with pitch {pitch} risks overlap given PCB etching tolerance {spec.pcb_tolerance}")
    pad_len = (Z - G) / 2
    pad_x = (Z + G) / 4

    pin_width = W.nominal
    pin_len = T.nominal
    pin_x = (L.nominal - T.nominal) / 2

    hip_x = A.nominal / 2

    y = (num_pins / 2 - 0.5) * pitch

    def r(x, y, a):
        a = math.radians(a)
        return (x * math.cos(a) - y * math.sin(a),
                x * math.sin(a) + y * math.cos(a))

    def rd(w, h, a):
        if a / 90 % 2 == 0:
            return w, h
        return h, w

    for n in range(start_pin, start_pin + num_pins):
        ret.features.append(
            Drawing.Pad(number=n,
                        center=r(-pad_x, y, rotation),
                        size=rd(pad_len, pad_width, rotation),
                        obround=(n != 1)))
        if n == 1:
            ret.features.append(Drawing.Circle(
                layer=Drawing.Layer.Silkscreen,
                center=(-pad_x - pad_len / 2 - 2 * PenWidth, y),
                radius=0.1))
        ret.features.append(
            Drawing.Line(
                layer=Drawing.Layer.Assembly,
                points=[
                    r(-pin_x + pin_len / 2, y + pin_width / 2, rotation),
                    r(-pin_x - pin_len / 2, y + pin_width / 2, rotation),
                    r(-pin_x - pin_len / 2, y - pin_width / 2, rotation),
                    r(-pin_x + pin_len / 2, y - pin_width / 2, rotation),
                    r(-pin_x + pin_len / 2, y + pin_width / 2, rotation),
                ],
                width=AssemblyPenWidth))

        if hip_x < pin_x - (pin_len / 2):
            k = pin_x - pin_len / 2
            ret.features.append(
                Drawing.Line(
                    layer=Drawing.Layer.Assembly,
                    points=[
                        r(-hip_x, y + pin_width / 2, rotation),
                        r(-k, y + pin_width / 2, rotation),
                        r(-k, y - pin_width / 2, rotation),
                        r(-hip_x, y - pin_width / 2, rotation),
                    ],
                    width=AssemblyPenWidth))

        y -= pitch


def _ild_silkscreen(ret, spec, A, B, LA, LB, T, pitch, pins_leftright, pins_updown):
    x, y = A.nominal, B.nominal
    x2, y2 = None, None

    if (x >= spec.InnerPadSpan(LA, T) - PenWidth and
        x <= spec.OuterPadSpan(LA, T) + PenWidth):
        # Vertical silkscreen would overlap with the L/R pins, so pull
        # back to just corner notches.
        y2 = pins_leftright * pitch + 2 * PenWidth
        # Oops, the L/R pads come too close to the T/B edges. Pull the
        # entire outline out.
        y = max(y2, y)
    if (pins_updown > 0 and
        y >= spec.InnerPadSpan(LB, T) - PenWidth and
        y <= spec.OuterPadSpan(LB, T) + PenWidth):
        x2 = pins_updown * pitch + 2 * PenWidth
        x = max(x2, x)

    if x2 is None:
        ret.features.append(Drawing.Line(
            layer=Drawing.Layer.Silkscreen,
            points=[(-x / 2, y / 2), (x / 2, y / 2)],
            width=PenWidth))
        ret.features.append(Drawing.Line(
            layer=Drawing.Layer.Silkscreen,
            points=[(-x / 2, -y / 2), (x / 2, -y / 2)],
            width=PenWidth))
    else:
        ret.features.append(Drawing.Line(
            layer=Drawing.Layer.Silkscreen,
            points=[(-x / 2, y / 2), (-x2 / 2, y / 2)],
            width=PenWidth))
        ret.features.append(Drawing.Line(
            layer=Drawing.Layer.Silkscreen,
            points=[(x / 2, y / 2), (x2 / 2, y / 2)],
            width=PenWidth))
        ret.features.append(Drawing.Line(
            layer=Drawing.Layer.Silkscreen,
            points=[(-x / 2, -y / 2), (-x2 / 2, -y / 2)],
            width=PenWidth))
        ret.features.append(Drawing.Line(
            layer=Drawing.Layer.Silkscreen,
            points=[(x / 2, -y / 2), (x2 / 2, -y / 2)],
            width=PenWidth))

    if y2 is None:
        ret.features.append(Drawing.Line(
            layer=Drawing.Layer.Silkscreen,
            points=[(-x / 2, y / 2), (-x / 2, -y / 2)],
            width=PenWidth))
        ret.features.append(Drawing.Line(
            layer=Drawing.Layer.Silkscreen,
            points=[(x / 2, y / 2), (x / 2, -y / 2)],
            width=PenWidth))
    else:
        ret.features.append(Drawing.Line(
            layer=Drawing.Layer.Silkscreen,
            points=[(-x / 2, y / 2), (-x / 2, y2 / 2)],
            width=PenWidth))
        ret.features.append(Drawing.Line(
            layer=Drawing.Layer.Silkscreen,
            points=[(-x / 2, -y / 2), (-x / 2, -y2 / 2)],
            width=PenWidth))
        ret.features.append(Drawing.Line(
            layer=Drawing.Layer.Silkscreen,
            points=[(x / 2, y / 2), (x / 2, y2 / 2)],
            width=PenWidth))
        ret.features.append(Drawing.Line(
            layer=Drawing.Layer.Silkscreen,
            points=[(x / 2, -y / 2), (x / 2, -y2 / 2)],
            width=PenWidth))


def in_line_pin_device(A, B, LA, LB, T, W, pitch, pins_leftright, pins_updown, spec):
    """Returns drawing for a dual/quad in-line symmetric device.

    This is a generic footprint builder that will accept any
    LandPatternSize.
    """
    ret = Drawing()

    _pin_line(ret=ret, spec=spec, A=A, L=LA, T=T, W=W, pitch=pitch,
              start_pin=1, num_pins=pins_leftright, rotation=0)
    _pin_line(ret=ret, spec=spec, A=B, L=LB, T=T, W=W, pitch=pitch,
              start_pin=pins_leftright + 1,
              num_pins=pins_updown, rotation=90)
    _pin_line(ret=ret, spec=spec, A=A, L=LA, T=T, W=W, pitch=pitch,
              start_pin=pins_leftright + pins_updown + 1,
              num_pins=pins_leftright, rotation=180)
    _pin_line(ret=ret, spec=spec, A=B, L=LB, T=T, W=W, pitch=pitch,
              start_pin=2 * pins_leftright + pins_updown + 1,
              num_pins=pins_updown, rotation=270)

    ret.features += [
        Drawing.Line(
            layer=Drawing.Layer.Assembly,
            points=[(A.nominal / 2, B.nominal / 2),
                    (A.nominal / 2, -B.nominal / 2),
                    (-A.nominal / 2, -B.nominal / 2),
                    (-A.nominal / 2, B.nominal / 2),
                    (A.nominal / 2, B.nominal / 2)],
            width=AssemblyPenWidth),

        Drawing.Line(
            layer=Drawing.Layer.Documentation,
            points=[(A.nominal / 8, 0), (-A.nominal / 8, 0)],
            width=PenWidth),
        Drawing.Line(
            layer=Drawing.Layer.Documentation,
            points=[(0, A.nominal / 8), (0, -A.nominal / 8)],
            width=PenWidth),
    ]

    _ild_silkscreen(ret, spec, A, B, LA, LB, T, pitch, pins_leftright, pins_updown)
    _courtyard(ret, spec)
    return ret


def sot23_3(A, B, L, T, W, pitch, spec):
    ret = Drawing()

    _pin_line(ret,
              spec=spec,
              A=A, L=L, T=T, W=W,
              pitch=2 * pitch,
              start_pin=1,
              num_pins=2,
              rotation=0)
    _pin_line(ret,
              spec=spec,
              A=A, L=L, T=T, W=W,
              pitch=pitch,
              start_pin=3,
              num_pins=1,
              rotation=180)

    G = spec.InnerPadSpan(L, T)
    X = spec.PadWidth(W)

    ret.features.extend([
        Drawing.Line(
            layer=Drawing.Layer.Assembly,
            points=[
                (-A.nominal / 2, -B.nominal / 2),
                (A.nominal / 2, -B.nominal / 2),
                (A.nominal / 2, B.nominal / 2),
                (-A.nominal / 2, B.nominal / 2),
                (-A.nominal / 2, -B.nominal / 2),
            ],
            width=AssemblyPenWidth),

        Drawing.Line(
            layer=Drawing.Layer.Silkscreen,
            points=[
                (-G / 2 + PenWidth, B.nominal / 2),
                (A.nominal / 2, B.nominal / 2),
                (A.nominal / 2, X / 2 + PenWidth),
            ],
            width=PenWidth),
        Drawing.Line(
            layer=Drawing.Layer.Silkscreen,
            points=[
                (-G / 2 + PenWidth, -B.nominal / 2),
                (A.nominal / 2, -B.nominal / 2),
                (A.nominal / 2, -X / 2 - PenWidth),
            ],
            width=PenWidth),
        Drawing.Line(
            layer=Drawing.Layer.Silkscreen,
            points=[(-A.nominal / 2, X / 2), (-A.nominal / 2, -X / 2)],
            width=PenWidth),

        Drawing.Line(
            layer=Drawing.Layer.Documentation,
            points=[(-A.nominal / 4, 0), (A.nominal / 4, 0)],
            width=PenWidth),
        Drawing.Line(
            layer=Drawing.Layer.Documentation,
            points=[(0, -A.nominal / 4), (0, A.nominal / 4)],
            width=PenWidth),
    ])
    _courtyard(ret, spec)
    return ret


def sot23_5(A, B, L, T, W, pitch, spec):
    ret = Drawing()
    _pin_line(ret,
              spec=spec,
              A=A, L=L, T=T, W=W,
              pitch=pitch,
              start_pin=1,
              num_pins=3,
              rotation=0)
    _pin_line(ret,
              spec=spec,
              A=A, L=L, T=T, W=W,
              pitch=2 * pitch,
              start_pin=4,
              num_pins=2,
              rotation=180)

    _ild_silkscreen(ret, spec, A, B, L, B, T, pitch, 3, 0)

    ret.features.extend([
        Drawing.Line(
            layer=Drawing.Layer.Assembly,
            points=[
                (-A.nominal / 2, -B.nominal / 2),
                (A.nominal / 2, -B.nominal / 2),
                (A.nominal / 2, B.nominal / 2),
                (-A.nominal / 2, B.nominal / 2),
                (-A.nominal / 2, -B.nominal / 2),
            ],
            width=AssemblyPenWidth),

        Drawing.Line(
            layer=Drawing.Layer.Documentation,
            points=[(-A.nominal / 4, 0), (A.nominal / 4, 0)],
            width=PenWidth),
        Drawing.Line(
            layer=Drawing.Layer.Documentation,
            points=[(0, -A.nominal / 4), (0, A.nominal / 4)],
            width=PenWidth),
    ])
    _courtyard(ret, spec)
    return ret

# TODO: TO252. DPAKs have a weird shape and the controlling dimensions
# are annoyingly not very amenable to use of the IPC constants,
# grmbl. Maybe it's better to put them exclusively in the JEDEC
# package, and improvise the construction there.

# TODO: SOT343. Annoyingly asymmetric construction where a single pad
# has different dimensions. Is it rare enough that it can just be left
# as an exercise to the reader using LandPatternSize's math functions?


class Drawing:
    """Container for drawn footprint features."""

    def __init__(self):
        self.features = []

    @property
    def length(self):
        (xmin, xmax), _ = self.bounding_box
        return xmax - xmin

    @property
    def width(self):
        _, (ymin, ymax) = self.bounding_box
        return ymax - ymin

    @property
    def bounding_box(self):
        xmin, xmax = 0, 0
        ymin, ymax = 0, 0
        for f in self.features:
            if isinstance(f, Drawing.Line):
                for p in f.points:
                    xmin = min(xmin, p[0] - f.width / 2)
                    xmax = max(xmax, p[0] + f.width / 2)
                    ymin = min(ymin, p[1] - f.width / 2)
                    ymax = max(ymax, p[1] + f.width / 2)
            elif isinstance(f, Drawing.Circle):
                xmin = min(xmin, f.center[0] - f.radius)
                xmax = max(xmax, f.center[0] + f.radius)
                ymin = min(ymin, f.center[1] - f.radius)
                ymax = max(ymax, f.center[1] + f.radius)
            elif isinstance(f, Drawing.Pad):
                xmin = min(xmin, f.center[0] - f.size[0] / 2)
                xmax = max(xmax, f.center[0] + f.size[0] / 2)
                ymin = min(ymin, f.center[1] - f.size[1] / 2)
                ymax = max(ymax, f.center[1] + f.size[1] / 2)
            else:
                raise RuntimeError("Unexpected drawing feature type")
        return (xmin, xmax), (ymin, ymax)

    def scale(self, s):
        for f in self.features:
            if isinstance(f, Drawing.Line):
                f.points = [(x * s, y * s) for x, y in f.points]
                f.width *= s
            elif isinstance(f, Drawing.Circle):
                f.center = (f.center[0] * s, f.center[1] * s)
                f.radius *= s
            elif isinstance(f, Drawing.Pad):
                f.center = (f.center[0] * s, f.center[1] * s)
                f.size = (f.size[0] * s, f.size[1] * s)
        return self

    def svg(self, background_color="black", copper_color="red", silkscreen_color="white", assembly_color="yellow", documentation_color="blue", courtyard_color="magenta"):
        """Output an IPC footprint drawing as an SVG file.
        
        This is mostly for debugging and pretty pictures in
        documentation.
        """
        (xmin, xmax), (ymin, ymax) = self.bounding_box
        w, h = xmax - xmin, ymax - ymin
        out = [
            '<svg xmlns="http://www.w3.org/2000/svg" version="1.1">',
            f'<g transform="translate({-xmin}, {-ymin})">',
            f'<rect x="{xmin}" y="{-ymax}" width="{w}" height="{h}" fill="{background_color}" />',
        ]
        colormap = {
            Drawing.Layer.Silkscreen: silkscreen_color,
            Drawing.Layer.Assembly: assembly_color,
            Drawing.Layer.Documentation: documentation_color,
            Drawing.Layer.Courtyard: courtyard_color,
        }
        for f in self.features:
            if isinstance(f, Drawing.Line):
                pts = [f"{x},{-y}" for x, y in f.points]
                opacity = 1 if f.layer == Drawing.Layer.Silkscreen else 0.6
                out.append(
                    '<polyline points="{0}" stroke="{1}" stroke-width="{2}" opacity="{3}" fill="none" stroke-linecap="round" />'.format(
                        " ".join(pts), colormap[f.layer], f.width, opacity))
            elif isinstance(f, Drawing.Circle):
                out.append(
                    f'<circle cx="{f.center[0]}" cy="{-f.center[1]}" r="{f.radius}" fill="{colormap[f.layer]}" opacity="0.8" />')
            elif isinstance(f, Drawing.Pad):
                out.append(
                    '<rect x="{0}" y="{1}" width="{2}" height="{3}" rx="{4}" ry="{4}" fill="{5}" opacity="0.8" />'.format(
                        f.center[0] - f.size[0] / 2, -(f.center[1] + f.size[1] / 2),
                        f.size[0], f.size[1],
                        min(f.size[0], f.size[1]) / 2 if f.obround else 0,
                        copper_color))
            else:
                raise RuntimeError("Unknown drawing feature type")
        out += [
            "</g>",
            "</svg>",
        ]
        return "\n".join(out)

    Layer = Enum(
        "Layer", ["Silkscreen", "Courtyard", "Assembly", "Documentation"])

    class Line:
        def __init__(self, layer, points, width):
            self.layer = layer
            self.points = points
            self.width = width

    class Circle:
        def __init__(self, layer, center, radius):
            self.layer = layer
            self.center = center
            self.radius = radius

    class Pad:
        def __init__(self, number, center, size, obround=False):
            self.number = number
            self.center = center
            self.size = size
            # Drawing suggestion: obround shape preferred if True,
            # else square.
            self.obround = obround


class Dimension:
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
        return cls(nominal - minus, nominal + plus)

    @property
    def tolerance(self):
        """The tolerance is the min-max delta of the Dimension."""
        return self.max - self.min

    @property
    def nominal(self):
        """The nominal value of the Dimension, assuming equal plus and minus tolerance."""
        return self.min + (self.tolerance / 2)


class LandPatternSize:
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
        return self._round_up(L.min + 2 * self.toe + _rms(L.tolerance, self.pcb_tolerance, self.place_tolerance))

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
        S = Dimension(L.min - 2 * T.max + rms / 2,
                      L.max - 2 * T.min - rms / 2)
        # and use it to calculate G(min).
        Gmin = self._round_down(S.max - 2 * self.heel - _rms(S.tolerance, self.pcb_tolerance, self.place_tolerance))
        if Gmin <= 0:
            raise InfeasibleFootprint(f"Inner pad span is {Gmin}, pads will short together")
        return Gmin

    def PadWidth(self, W):
        """Returns the pad width given component pin width.

        This dimension is called X_max in the standard.
        """
        return self._round_up(W.min + 2 * self.side + _rms(W.tolerance, self.pcb_tolerance, self.place_tolerance))

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
        Smin = L.min - 2 * T.max
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
    print(x)
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
