from __future__ import with_statement
from __future__ import division
from __future__ import absolute_import
import kidraw

class _Feature(object):
    def __init__(self, dir, num_slots):
        self.nslots = num_slots
        self.dir = dir
            
class _Pin(_Feature):
    def __init__(self, numbers, dir):
        super(_Pin, self).__init__(dir=dir, num_slots=1)
        self._numbers = numbers
        self._active_low = False
        self._clock = False

    def active_low(self):
        self._active_low, self._clock = True, False

    def clock(self):
        self._active_low, self._clock = False, True

    def draw(self, s):
        r = s.pin(*self._numbers)
        if self._active_low:
            r.active_low()
        if self._clock:
            r.clock()
        return r

class _Gap(_Feature):
    pass

class _Expando(_Gap):
    pass

class ICBuilder(object):
    def __init__(self):
        self._font_size = 50
        self._pin_len = 200
        self._dir = None
        self._slot_spacing = 200
        self._features = []

    def font_size(self, s):
        self._font_size = s
        return self

    def pin_len(self, l):
        self._pin_len = l
        return self
        
    def dir(self, d):
        self._dir = d
        return self

    def slot_spacing(self, s):
        self._slot_spacing = s
        return self
        
    def pin(self, *numbers):
        self._features.append(_Pin(numbers, self._dir))
        return self._features[-1]

    def gap(self, gap=1):
        self._features.append(_Gap(self._dir, gap))
        return self._features[-1]

    def expando(self):
        self._features.append(_Expando(self._dir, 1))
        return self._features[-1]

    def build(self, s):
        features = {
            kidraw.RIGHT: [f for f in self._features if f.dir == kidraw.RIGHT],
            kidraw.LEFT: [f for f in self._features if f.dir == kidraw.LEFT],
            kidraw.UP: [f for f in self._features if f.dir == kidraw.UP],
            kidraw.DOWN: [f for f in self._features if f.dir == kidraw.DOWN],
        }
        nslots = dict((k, sum([x.nslots for x in v])) for k, v in features.items())
        slots_wide = max(nslots[kidraw.UP], nslots[kidraw.DOWN])-1
        slots_high = max(nslots[kidraw.RIGHT], nslots[kidraw.LEFT])-1
        margin = self._slot_spacing
        # TODO: muck about with the expandos to center
        with s.save_position():
            s.translate(-slots_wide/2*self._slot_spacing-margin-self._pin_len,
                        slots_high/2*self._slot_spacing)
            with s.save_position():
                for f in features[kidraw.RIGHT]:
                    if isinstance(f, _Pin):
                        f.draw(s).len(self._pin_len).font_size(self._font_size).dir(f.dir)
                    s.translate(0, -f.nslots*self._slot_spacing)

            s.translate(slots_wide*self._slot_spacing + 2*margin + 2*self._pin_len, 0)
            with s.save_position():
                for f in features[kidraw.LEFT]:
                    if isinstance(f, _Pin):
                        f.draw(s).len(self._pin_len).font_size(self._font_size).dir(f.dir)
                    s.translate(0, -f.nslots*self._slot_spacing)
                
            s.translate(-slots_wide*self._slot_spacing - self._pin_len - margin,
                        margin + self._pin_len)
            with s.save_position():
                for f in features[kidraw.DOWN]:
                    if isinstance(f, _Pin):
                        f.draw(s).len(self._pin_len).font_size(self._font_size).dir(f.dir)
                    s.translate(f.nslots*self._slot_spacing, 0)

            s.translate(0, -slots_high*self._slot_spacing - 2*margin - 2*self._pin_len)
            with s.save_position():
                for f in features[kidraw.UP]:
                    if isinstance(f, _Pin):
                        f.draw(s).len(self._pin_len).font_size(self._font_size).dir(f.dir)
                    s.translate(f.nslots*self._slot_spacing, 0)

            s.translate(-margin, self._pin_len)
            s.rect((0, 0),
                   (slots_wide*self._slot_spacing + 2*margin,
                    slots_high*self._slot_spacing + 2*margin))
