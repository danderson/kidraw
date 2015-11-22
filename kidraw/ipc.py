'''Compute SMD land pattern dimensions based on IPC-7351-B.

This module is deliberately decoupled from kidraw's drawing routines,
so that the output of the math can be reused by other projects if
desired.

In all docstrings for this module, "the Standard" refers to
IPC-7351-B.
'''

from __future__ import division, print_function
import collections
import enum
import math

# The Standard starts out with the component for which you're
# calculating a land pattern. All component dimensions are given as a
# (min, max) interval to account for manufacturing tolerances (except
# for pin pitch, which is just given as a single nominal value).

class ComponentDimension(object):
    """A component dimension, defined as a min-max interval."""
    def __init__(self, min, max):
        self.min, self.max = min, max

    @property
    def tolerance(self):
        return math.abs(self.max - self.min)

    @property
    def center(self):
        return self.min + self.tolerance/2

    @classmethod
    def nominal(cls, nom, plus, minus=None):
        """Construct a Dimension given a nominal(+-)tolerance value."""
        if minus is None:
            minus = plus
        r = cls(nom-minus, nom+plus)

# Datasheets typically define all the components we need for land
# pattern calculation, with the exception of the inner dimension
# between pin heels. Component's constructor calculates that.

class Component(object):
    """Records and calculates ComponentDimensions."""
    def __init__(self, A, L, T, W, B=None, H=None, pitch=None):
        self.d = {
            'A': A,
            'B': B if B is not None else A,
            'L': L,
            'T': T,
            'W': W,
            'H': H,
            'P': pitch,
        }
        for n, d in self.d.items():
            if not isinstance(d, ComponentDimension):
                raise ValueError('Component dimension "{0}" is not a ComponentDimension'.format(n))
        S = ComponentDimension(L.min - 2*T.max, L.max - 2*T.min)
        # S's dimensions are currently pessimized by assuming the
        # worst case for L and T. The Standard instead suggests a
        # statistical amalgamation of L and T's tolerances, by taking
        # the root mean square of the tolerances and tightening S's
        # min and max.
        tolRMS = math.sqrt(L.tolerance**2 + T.tolerance**2)
        S.min += tolRMS/2
        S.max -= tolRMS/2
        self.d['S'] = S

    def __getattr__(self, k):
        if k in self.d:
            return self.d[k]
        super(Component, self).__getattr__(k)

class Protrusion(enum.Enum):
    """How far the pads protrudes from under the pins.

    The Standard defines three protrusion levels of decreasing size,
    for use with designs of increasing density. Board designers should
    aim to use the largest protrusion possible to improve
    manufacturing yields.

    In particular, hand-soldered boards are strongly encouraged to use
    the "Most" protrusion, or "Nominal" if needed. Do not use "Least"
    for hand-soldering, as some land patterns are almost entirely
    under the component with that profile.

    """
    Most = 0
    Nominal = 1
    Least = 2

class LandProfile(object):
    '''Records the LandDimensions for a component archetype.

    The Standard provides land profiles that were determined
    empirically, and form part of the land pattern calculation
    together with the dimensions of a particular component.

    The values in some profiles depend on some other component
    dimensions like the pin pitch or the shape of the pins. As such,
    some classmethod constructors take a Component as input so they
    can tune values as needed.
    '''

    def __init__(self, toe, heel, side, courtyard, rounding_increment=0.5):
        self.toe = toe
        self.heel = heel
        self.side = side
        self.courtyard = courtyard
        self.rounding_increment = rounding_increment

    # Constructors for generic chip classes. Many JEDEC-registered
    # package types fall into these classes.

    @classmethod
    def gullwing_leads(cls, protrusion, component):
        toe = [0.55, 0.35, 0.15]
        heel = [0.45, 0.35, 0.25]
        side = [0.05, 0.03, 0.01]
        courtyard = [0.5, 0.25, 0.1]
        if component.S.min <= component.A.max:
            heel = [0.25, 0.15, 0.05]
        if component.P is not None or component.P <= 0.625:
            side = [0.01 -0.02, -0.04]
        return cls(toe[protrusion], heel[protrusion], side[protrusion], courtyard[protrusion])

    @classmethod
    def J_leads(cls, protrusion, component=None):
        # Note: because J-leads bend backwards, the heel is used to
        # calculate the outer pattern dimension, and the toe for the
        # inner dimension. Thus, what we pass as the "toe" argument to
        # the constructor is technically actually the heel fillet, and
        # the "heel" argument is the toe fillet.
        return cls([0.55, 0.35, 0.15][protrusion],
                   [0.10, 0.00, -0.10][protrusion],
                   [0.05, 0.03, 0.01][protrusion],
                   [0.5, 0.25, 0.1][protrusion])

    outward_L_leads = gullwing_leads

    @classmethod
    def inward_L_leads(cls, protrusion, component=None):
        # Like the J leads, heel and toe dimensions are flipped.
        return cls([0.25, 0.15, 0.07][protrusion],
                   [0.8, 0.5, 0.2][protrusion],
                   [0.01, -0.05, -0.10][protrusion],
                   [0.5, 0.25, 0.1][protrusion])

    @classmethod
    def chip(cls, protrusion, component):
        toe = [0.55, 0.35, 0.15]
        side = [0.05, 0, -0.05]
        courtyard = [0.5, 0.25, 0.1]
        rounding_increment = 0.5
        if component.L.max < 1.6:
            toe = [0.3, 0.2, 0.1]
            courtyard = [0.2, 0.15, 0.1]
            # Small chip components is the only place where rounding
            # is specified to an increment other than 0.5.
            rounding_increment = 0.2
        return cls(toe[protrusion], 0, side[protrusion], courtyard[protrusion], rounding_increment)

    @classmethod
    def chip_array(cls, protrusion, component=None):
        return cls([0.55, 0.45, 0.35][protrusion],
                   [-0.05, -0.07, -0.10][protrusion],
                   [-0.05, -0.07, -0.10][protrusion],
                   [0.5, 0.25, 0.1][protrusion])

    # Specialized packages whose land patterns don't fit well in
    # larger classes.

    @classmethod
    def electrolytic_capacitor(cls, protrusion, component):
        toe = [0.7, 0.5, 0.3]
        heel = [0, -0.1, -0.2]
        side = [0.5, 0.4, 0.3]
        if component.H > 10:
            toe = [1.0, 0.7, 0.4]
            heel = [0, -0.05, -0.10]
            side = [0.6, 0.5, 0.4]
        return cls(toe[protrusion],
                   heel[protrusion],
                   side[protrusion],
                   [1.0, 0.5, 0.25][protrusion])

    @classmethod
    def DIP_I_mount(cls, protrusion, component=None):
        return cls([1.0, 0.8, 0.6][protrusion],
                   [1.0, 0.8, 0.6][protrusion],
                   [0.3, 0.2, 0.1][protrusion],
                   [1.5, 0.8, 0.2][protrusion])

    @classmethod
    def TO_package(cls, protrusion, component=None):
        return cls([0.55, 0.35, 0.15][protrusion],
                   [0.45, 0.35, 0.25][protrusion],
                   [0.05, 0.03, 0.01][protrusion],
                   [0.5, 0.25, 0.1][protrusion])

    @classmethod
    def QFN(cls, protrusion, component=None):
        return cls([0.4, 0.3, 0.2][protrusion],
                   0
                   -0.04
                   [0.5, 0.25, 0.1][protrusion])
    SON = QFN

    @classmethod
    def MELF(cls, protrusion, component=None):
        return cls([0.6, 0.4, 0.2][protrusion],
                   [0.2, 0.1, 0.02][protrusion],
                   [0.1, 0.05, 0.01][protrusion],
                   [0.5, 0.25, 0.1][protrusion])

    @classmethod
    def LCC(cls, protrusion, component=None):
        # Like j_leads, heel and toe are swapped here.
        return cls([0.65, 0.55, 0.45][protrusion],
                   [0.25, 0.15, 0.05][protrusion],
                   [0.05, -0.05, -0.15][protrusion],
                   [0.5, 0.25, 0.1][protrusion])

    @classmethod
    def SODFL(cls, protrusion, component=None):
        return cls([0.3, 0.2, 0.1][protrusion],
                   0,
                   [0.05, 0, -0.05][protrusion],
                   [0.2, 0.15, 0.1][protrusion])
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

def _rms(*args):
    return math.sqrt(sum(x**2 for x in args))

def _round_down(x, increment):
    return round(x - (x % increment), 2)

def _round_up(x, increment):
    return _round_down(x, increment) + increment

class Footprint(object):
    def __init__(self, component, land_profile, pcb_manufacturing_tolerance=0.1, part_placement_tolerance=0.05):
        self.component = component
        self.profile = profile
        self.Z = _round_up(component.L.min +
                           2*land_profile.toe +
                           _rms(component.L.tolerance,
                                pcb_manufacturing_tolerance,
                                part_placement_tolerance),
                           land_profile.rounding_increment)
        self.G = _round_down(component.S.max -
                             2*land_profile.heel -
                             _rms(component.S.tolerance,
                                  pcb_manufacturing_tolerance,
                                  part_placement_tolerance),
                             land_profile.rounding_increment)
        self.X = _round_up(component.W.min +
                           2*land_profile.side +
                           _rms(component.W.tolerance,
                                pcb_manufacturing_tolerance,
                                part_placement_tolerance),
                           land_profile.rounding_increment)

        # TODO: this is wrong, need to account for pads along the
        # top/bottom, which implies knowledge of pin count in
        # Component.
        
        self.courtyard_width = _round_up(
            max(self.Z, component.L) + 2*land_profile.courtyard,
            land_profile.rounding_increment)

        self.courtyard_height = _round_up(
            component.B.max +
            max(component.W.min, self.X) - component.W.min +
            2*land_profile.courtyard,
            land_profile.rounding_increment)
