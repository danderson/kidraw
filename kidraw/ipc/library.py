"""Library of IPC7351 land patterns.

This library provides reference footprints for common parts like chip
resistors, for designs that just need a "generic 0805" land pattern
that will probably work.

It also provides shorthands for common chip packages, to simplify
their construction.
"""

from kidraw import ipc

Most = ipc.LandPatternSize.Most
Nominal = ipc.LandPatternSize.Nominal
Least = ipc.LandPatternSize.Least

_chip_metric_dimensions = {
    "1005": (ipc.Dimension.from_nominal(1.00, 0.05),
             ipc.Dimension.from_nominal(0.50, 0.05),
             ipc.Dimension.from_nominal(0.2, 0.10)),
    "1608": (ipc.Dimension.from_nominal(1.55, 0.05),
             ipc.Dimension.from_nominal(0.85, 0.10),
             ipc.Dimension.from_nominal(0.3, 0.15, 0.20)),
    "2012": (ipc.Dimension.from_nominal(2.00, 0.10),
             ipc.Dimension.from_nominal(1.25, 0.15),
             ipc.Dimension.from_nominal(0.4, 0.1, 0.2)),
    "3216": (ipc.Dimension.from_nominal(3.20, 0.1, 0.2),
             ipc.Dimension.from_nominal(1.60, 0.15),
             ipc.Dimension.from_nominal(0.50, 0.25)),
}


def metric(n):
    return _chip_metric_dimensions[n]


_chip_imperial_dimensions = {
    "0402": metric("1005"),
    "0603": metric("1608"),
    "0805": metric("2012"),
    "1206": metric("3216"),
}


def imperial(n):
    return _chip_imperial_dimensions[n]


def chip(profile, size, polarized=False):
    """Construct a land pattern for chip devices.

    >>> chip(Most, metric('2012'), polarized=True)

    >>> chip(Most, metric('0402'), polarized=True)
    """
    A, B, T = size
    return ipc.two_terminal_symmetric_device(
        A, B, A, T, B, ipc.LandPatternSize.chip(profile, A), polarized)


def SOIC(profile, A, B, L, T, W, num_pins, pitch=1.27):
    """Construct a land pattern for a SOIC device.

    SOIC unfortunately lacks standardized dimensions (or rather, there
    are 3-4 "standard" dimensions to pick from). Because of this, the
    only default dimension provided is the one everyone seems to agree
    on, 1.27mm pitch - but check that, some ICs are sold as SOIC with
    finer pitch.
    """
    if num_pins % 2 != 0:
        raise ValueError("num_pins must be even for SOIC devices")
    return ipc.in_line_pin_device(
        A=A, B=B, LA=L, LB=B, T=T, W=W, pitch=pitch,
        pins_leftright=int(num_pins / 2), pins_updown=0,
        spec=ipc.LandPatternSize.SOIC(
            profile=profile, A=A, L=L, T=T, pitch=pitch))


SOP = SOIC


def SOT23(profile, num_pins):
    """Construct a land pattern for a SOT23 device.
    
    Supports 3, 5, 6 and 8-pin devices, with dimensions from JEDEC
    TO-236 and MO-178.
    """
    if num_pins == 3:
        # Dimensions from JEDEC TO-236-A[AB]
        A = ipc.Dimension(1.2, 1.4)
        B = ipc.Dimension(2.8, 3.04)
        L = ipc.Dimension(2.1, 2.64)
        T = ipc.Dimension(0.4, 0.6)
        W = ipc.Dimension(0.3, 0.5)
        return ipc.sot23_3(
            A, B, L, T, W, 0.95,
            ipc.LandPatternSize.SOT(profile, A, L, T, 0.95))
    if num_pins == 5:
        # Dimensions from JEDEC MO-178-C variant AA
        A = ipc.Dimension.from_nominal(1.6, 0.1)
        B = ipc.Dimension.from_nominal(2.9, 0.1)
        L = ipc.Dimension.from_nominal(2.8, 0.2)
        T = ipc.Dimension(0.3, 0.6)
        W = ipc.Dimension(0.3, 0.5)
        return ipc.sot23_5(
            A, B, L, T, W, 0.95,
            ipc.LandPatternSize.SOT(profile, A, L, T, 0.95))
    if num_pins == 6:
        # Dimensions from JEDEC MO-178-C variant AB
        A = ipc.Dimension.from_nominal(1.6, 0.1)
        B = ipc.Dimension.from_nominal(2.9, 0.1)
        L = ipc.Dimension.from_nominal(2.8, 0.2)
        T = ipc.Dimension(0.3, 0.6)
        W = ipc.Dimension(0.3, 0.5)
        return ipc.in_line_pin_device(
            A, B, L, B, T, W, 0.95, 3, 0,
            ipc.LandPatternSize.SOT(profile, A, L, T, 0.95))
    if num_pins == 8:
        # Dimensions from JEDEC MO-178-C variant BA
        A = ipc.Dimension.from_nominal(1.6, 0.1)
        B = ipc.Dimension.from_nominal(2.9, 0.1)
        L = ipc.Dimension.from_nominal(2.8, 0.2)
        T = ipc.Dimension(0.3, 0.6)
        W = ipc.Dimension(0.22, 0.38)
        # SOT23-8 is almost at the threshold where IPC switches to
        # much smaller side fillets. This causes overlap violations
        # with the Most profile. As such, we force the narrower pitch
        # profile here by using a smaller pitch.
        spec = ipc.LandPatternSize.SOT(profile, A, L, T, 0.6)
        return ipc.in_line_pin_device(
            A, B, L, B, T, W, 0.65, 4, 0, spec)
    raise ValueError(f"No known standard dimensions for SOT23-{num_pins}")


def SC70(profile, num_pins):
    """Construct a land pattern for an SC70 device.
    
    Supports 5, 6 and 8-pin devices, with dimensions from JEDEC
    MO-203.
    """
    A = ipc.Dimension.from_nominal(1.25, 0.15)
    B = ipc.Dimension.from_nominal(2, 0.15)
    L = ipc.Dimension.from_nominal(2.1, 0.3)
    T = ipc.Dimension(0.26, 0.46)
    W = ipc.Dimension(0.15, 0.3)
    if num_pins == 5:
        # MO-203-C variant AA
        return ipc.sot23_5(
            A, B, L, T, W, 0.65,
            ipc.LandPatternSize.SOT(profile, A, L, T, 0.65))
    if num_pins == 6:
        # MO-203-C variant AB
        return ipc.in_line_pin_device(
            A, B, L, B, T, W, 0.65, 3, 0,
            ipc.LandPatternSize.SOT(profile, A, L, T, 0.65))
    if num_pins == 8:
        # MO-203-C variant BA
        W = ipc.Dimension(0.15, 0.27)
        spec = ipc.LandPatternSize.SOT(profile, A, L, T, 0.5)
        return ipc.in_line_pin_device(
            A, B, L, B, T, W, 0.5, 4, 0, spec)
    raise ValueError(f"No known standard dimensions for SOT23-{num_pins}")


def QFP(profile, A, L, T, W, pitch, num_pins):
    """Construct a land pattern for a QFP device.

    This builder assumes a square device with an equal number of pins
    on all sides. If you have an asymmetric package, use the lower
    level primitives to construct it.
    """
    if num_pins % 4 != 0:
        raise ValueError("num_pins must be a multiple of 4 for QFP devices")
    return ipc.in_line_pin_device(
        A, A, L, L, T, W, pitch, int(num_pins / 4), int(num_pins / 4),
        ipc.LandPatternSize.QFP(profile, A, L, T, pitch))


def QFN(profile, A, T, W, pitch, num_pins):
    """Construct a land pattern for a QFN device.

    This builder assumes a square device with an equal number of pins
    on all sides, with no lead pullback. If you have an asymmetric
    package or pulled back leads, use the lower level primitives to
    construct it.
    """
    if num_pins % 4 != 0:
        raise ValueError("num_pins must be a multiple of 4 for QFP devices")
    return ipc.in_line_pin_device(
        A, A, A, A, T, W, pitch, num_pins / 4, num_pins / 4,
        ipc.LandPatternSize.QFN(profile))
