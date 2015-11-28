import math
from copy import deepcopy
from enum import Enum

from kidraw import ipc

class Layer(Enum):
    TopCopper = 'F.Cu'
    TopSilkscreen = 'F.SilkS'
    TopPasteMask = 'F.Paste'
    TopSolderMask = 'F.Mask'
    TopCourtyard = 'F.CrtYd'
    TopAssembly = 'F.Fab'
    BottomCopper = 'B.Cu'
    BottomSilkscreen = 'B.SilkS'
    BottomPasteMask = 'B.Paste'
    BottomSolderMask = 'B.Mask'
    BottomCourtyard = 'B.CrtYd'
    BottomAssembly = 'B.Fab'                

class PadShape(Enum):
    Circle = 'circle'
    Rectangle = 'rect'
    Obround = 'oval'
    # TODO: trapezoid

class _Struct(object):
    __attributes__ = {}

    def __init__(self, **kwargs):
        for k, v in self.__attributes__.items():
            setattr(self, k, deepcopy(v))
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __setattr__(self, k, v):
        if k not in self.__attributes__:
            raise ValueError('Not allowed to set {0} in this object'.format(k))
        super(_Struct, self).__setattr__(k, v)

class Text(_Struct):
    __attributes__ = {
        '_type': 'user',
        'text': '',
        'position': (0, 0),
        'layer': Layer.TopSilkscreen,
        'hidden': False,
        'font_size': (1, 1),
        'line_width': 0.15,
    }

    @property
    def bounding_box(self):
        w = len(text)*self.font_size
        return ((self.position[0]-w/2,
                 self.position[0]+w/2),
                (self.position[1]-self.font_size[1]/2,
                 self.position[1]+self.font_size[1]/2))

    def __str__(self):
        return '''(fp_text {0._type} "{0.text}"
  (at {0.position[0]} {0.position[1]})
  (layer {0.layer.value})
  {1}hide
  (effects
    (font
      (size {0.font_size[0]} {0.font_size[1]})
      (thickness {0.line_width})
    )
  )
)'''.format(self, '' if self.hidden else '#')

class Line(_Struct):
    __attributes__ = {
        'start': (0, 0),
        'end': (0, 0),
        'layer': Layer.TopSilkscreen,
        'line_width': 0.15,
    }

    @property
    def bounding_box(self):
        return ((min(self.start[0], self.end[0]),
                 max(self.start[0], self.end[0])),
                (min(self.start[1], self.end[1]),
                 max(self.start[1], self.end[1])))

    def __str__(self):
        return '''(fp_line
  (start {0.start[0]} {0.start[1]})
  (end {0.end[0]} {0.end[1]})
  (layer {0.layer.value})
  (width {0.line_width})
)'''.format(self)

class Circle(_Struct):
    __attributes__ = {
        'center': (0, 0),
        'radius': 0,
        'layer': Layer.TopSilkscreen,
        'line_width': 0.15,
    }

    @property
    def bounding_box(self):
        return ((self.center[0]-self.radius, self.center[0]+self.radius),
                (self.center[1]-self.radius, self.center[1]+self.radius))

    def __str__(self):
        end = (self.center[0]+self.radius, self.center[1])
        return '''(fp_circle
  (center {0.center[0]} {0.center[1]})
  (end {1[0]} {1[1]})
  (layer {0.layer.value})
  (width {0.line_width})
)'''.format(self, end)

class Arc(_Struct):
    __attributes__ = {
        'center': (0, 0),
        'radius': 0,
        'start_angle': 0,
        'end_angle': 0,
        'layer': Layer.TopSilkscreen,
        'line_width': 0.15,
    }

    @property
    def bounding_box(self):
        return ((self.center[0]-self.radius, self.center[0]+self.radius),
                (self.center[1]-self.radius, self.center[1]+self.radius))

    def __str__(self):
        end = (
            self.center[0] + math.sin(math.radians(self.start_angle)) * self.radius,
            self.center[1] + math.cos(math.radians(self.start_angle)) * self.radius)
        alpha = self.end_angle - self.start_angle
        return '''(fp_arc
  (start {0.center[0]} {0.center[1]})
  (end {1[0]} {1[1]})
  (angle {2})
  (layer {0.layer.value})
  (width {0.line_width})
)'''.format(self, end, alpha)

class Poly(_Struct):
    __attributes__ = {
        'points': [],
        'layer': Layer.TopSilkscreen,
        'line_width': 0.15
    }

    @property
    def bounding_box(self):
        xmin, xmax, ymin, ymax = 0, 0, 0, 0
        for p in self.points:
            xmin = min(xmin, p[0])
            xmax = max(xmax, p[0])
            ymin = min(ymin, p[1])
            ymax = max(ymax, p[1])
        return (xmin, xmax), (ymin, ymax)

    def __str__(self):
        pts = '\n'.join('    (xy {0} {1})'.format(x, y) for x, y in self.points)
        return '''(fp_poly
  (pts
    {1}
  )
  (layer {0.layer.value})
  (width {0.line_width})
)'''.format(self, pts)

# TODO: bezier curve, if I can find any use for one.

class ThroughHolePad(_Struct):
    __attributes__ = {
        'name': 0,
        'shape': PadShape.Circle,
        'center': (0, 0),
        'angle': 0,
        'size': (0, 0),
        'drill_size': 0,
        'clearance': 0,
        'solder_mask_margin': 0,
        'thermal_width': 0,
        'thermal_gap': 0,
    }

    @property
    def bounding_box(self):
        xmin = self.center[0]-self.size[0]/2-self.solder_mask_margin
        xmax = self.center[0]+self.size[0]/2+self.solder_mask_margin
        ymin = self.center[1]-self.size[1]/2-self.solder_mask_margin
        ymax = self.center[1]+self.size[1]/2+self.solder_mask_margin
        return (xmin, xmax), (ymin, ymax)
    
    def __str__(self):
        return '''(pad {0.name} thru_hole {0.shape.value}
  (at {0.center[0]} {0.center[1]} {0.angle})
  (size {0.size[0]} {0.size[1]})
  (drill {0.drill_size})
  (layers *.Cu *.Mask F.SilkS)
  (solder_mask_margin {0.solder_mask_margin})
  (clearance {0.clearance})
  {1}(zone_connect 1)
  {1}(thermal_width {0.thermal_width})
  {1}(thermal_gap {0.thermal_gap})
)'''.format(self, '#' if self.thermal_gap == 0 else '')

class SurfaceMountPad(_Struct):
    __attributes__ = {
        'name': 0,
        'shape': PadShape.Rectangle,
        'center': (0, 0),
        'angle': 0,
        'size': (0, 0),
        'clearance': 0,
        'solder_mask_margin': 0,
        'solder_paste_margin': 0,
        'solder_paste_ratio': 1,
        'thermal_width': 0,
        'thermal_gap': 0,
    }

    @property
    def bounding_box(self):
        xmin = self.center[0]-self.size[0]/2-self.solder_mask_margin
        xmax = self.center[0]+self.size[0]/2+self.solder_mask_margin
        ymin = self.center[1]-self.size[1]/2-self.solder_mask_margin
        ymax = self.center[1]+self.size[1]/2+self.solder_mask_margin
        return (xmin, xmax), (ymin, ymax)

    def __str__(self):
        ratio = int(-50*(1 - self.solder_paste_ratio))
        return '''(pad {0.name} smd {0.shape.value}
  (at {0.center[0]} {0.center[1]} {0.angle})
  (size {0.size[0]} {0.size[1]})
  (layers F.Cu F.Paste F.Mask)
  (solder_mask_margin {0.solder_mask_margin})
  (clearance {0.clearance})
  (solder_paste_margin {0.solder_paste_margin})
  (solder_paste_margin_ratio {1})
  {2}(zone_connect 1)
  {2}(thermal_width {0.thermal_width})
  {2}(thermal_gap {0.thermal_gap})
)'''.format(self, ratio, '#' if self.thermal_gap == 0 else '')

class TestPad(_Struct):
    __attributes__ = {
        'name': 0,
        'shape': PadShape.Circle,
        'center': (0, 0),
        'angle': 0,
        'size': (0, 0),
        'clearance': 0,
        'solder_mask_margin': 0,
    }

    @property
    def bounding_box(self):
        xmin = self.center[0]-self.size[0]/2-self.solder_mask_margin
        xmax = self.center[0]+self.size[0]/2+self.solder_mask_margin
        ymin = self.center[1]-self.size[1]/2-self.solder_mask_margin
        ymax = self.center[1]+self.size[1]/2+self.solder_mask_margin
        return (xmin, xmax), (ymin, ymax)
    
    def __str__(self):
        return '''(pad {0.name} connect {0.shape.value}
  (at {0.center[0]} {0.center[1]} {0.angle})
  (size {0.size[0]} {0.size[1]})
  (layers F.Cu F.Mask)
  (solder_mask_margin {0.solder_mask_margin})
  (clearance {0.clearance})
)'''.format(self)

class Connector(TestPad):
    pass

class Footprint(_Struct):
    __attributes__ = {
        'name': None,
        'description': '',
        'refdes': Text(_type='reference', position=None, text='REF', layer=Layer.TopSilkscreen),
        'value': Text(_type='value', position=None, text='VAL', layer=Layer.TopAssembly),
        'features': [],
    }

    @property
    def bounding_box(self):
        xmin, xmax, ymin, ymax = 0, 0, 0, 0
        for f in self.features:
            xmin = min(xmin, f.bounding_box[0][0])
            xmax = max(xmax, f.bounding_box[0][1])
            ymin = min(ymin, f.bounding_box[1][0])
            ymax = max(ymax, f.bounding_box[1][1])
        if self.refdes.position is not None:
            xmin = min(xmin, self.refdes.position[0])
            xmax = max(xmax, self.refdes.position[0])
            ymin = min(ymin, self.refdes.position[1])
            ymax = max(ymax, self.refdes.position[1])
        if self.value.position is not None:
            xmin = min(xmin, self.value.position[0])
            xmax = max(xmax, self.value.position[0])
            ymin = min(ymin, self.value.position[1])
            ymax = max(ymax, self.value.position[1])
        return (xmin, xmax), (ymin, ymax)

    @property
    def filename(self):
        return self.name.replace(' ', '_')
    
    def from_ipc(self, ipc_drawing):
        """Translate a kidraw.ipc Drawing into Footprint features."""
        for f in ipc_drawing.features:
            if isinstance(f, ipc.Drawing.Pad):
                self.features.append(SurfaceMountPad(
                    name=f.number,
                    shape=PadShape.Obround if f.obround else PadShape.Rectangle,
                    center=(f.center[0], -f.center[1]),
                    size=f.size))
            elif isinstance(f, ipc.Drawing.Line):
                layer = {
                    ipc.Drawing.Layer.Silkscreen: Layer.TopSilkscreen,
                    ipc.Drawing.Layer.Courtyard: Layer.TopCourtyard,
                    ipc.Drawing.Layer.Assembly: Layer.TopAssembly,
                    ipc.Drawing.Layer.Documentation: Layer.TopAssembly,
                }[f.layer]
                for a, b in zip(f.points, f.points[1:]):
                    self.features.append(Line(
                        start=(a[0], -a[1]),
                        end=(b[0], -b[1]),
                        layer=layer,
                        line_width=f.width))
            elif isinstance(f, ipc.Drawing.Circle):
                layer = {
                    ipc.Drawing.Layer.Silkscreen: Layer.TopSilkscreen,
                    ipc.Drawing.Layer.Courtyard: Layer.TopCourtyard,
                    ipc.Drawing.Layer.Assembly: Layer.TopAssembly,
                    ipc.Drawing.Layer.Documentation: Layer.TopAssembly,
                }[f.layer]
                # Hack: to draw a filled circle, we draw a zero-length
                # line of width == diameter.
                self.features.append(Line(
                    start=(f.center[0], -f.center[1]),
                    end=(f.center[0], -f.center[1]),
                    layer=layer,
                    line_width=2*f.radius))
            else:
                raise ValueError('Unknown IPC footprint feature type', type(f))
        return self
    
    def __str__(self):
        refdes = deepcopy(self.refdes)
        if refdes.position is None:
            refdes.position = (0, self.bounding_box[1][0]-1)
        value = deepcopy(self.value)
        if value.position is None:
            value.position = (0, self.bounding_box[1][1]+1)
        return '''(module {0.filename}
(layer F.Cu)
(tedit 0)
(at 0 0)
(descr "{0.description}")
{2}
{3}
{1}
)'''.format(self, '\n'.join(str(f) for f in self.features), refdes, value)
