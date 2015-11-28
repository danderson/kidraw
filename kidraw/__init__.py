from kidraw import schematic, footprint, ipc

class Library(object):
    def __init__(self, name):
        self._name = name
        self.devices = []

    def save(self):
        sch = [x.schematic.sch() for x in self.devices]
        doc = [x.schematic.doc() for x in self.devices]
        footprints = [(fn, str(f)) for fn, f in d.footprints.items() for d in self.devices]

class Device(object):
    def __init__(self, schematic=None, footprints=[]):
        self.schematic = schematic
        self.footprints = footprints
