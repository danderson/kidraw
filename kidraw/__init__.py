import shutil
import os
import os.path

from kidraw import schematic, footprint, ipc

class Library(object):
    def __init__(self, name):
        self._name = name
        self.devices = []

    def save(self):
        sch = [x.schematic.sch() for x in self.devices]
        doc = [x.schematic.doc() for x in self.devices]
        footprints = [(d.schematic.filename+'_'+f.filename, str(f)) for d in self.devices for f in d.footprints]

        with open(self._name+'.lib', 'w') as f:
            f.write('''EESchema-LIBRARY Version 2.3
#encoding utf-8
{0}
#End Library'''.format('\n'.join(sch)))
        with open(self._name+'.dcm', 'w') as f:
            f.write('''EESchema-DOCLIB  Version 2.0
{0}
#End Doc Library'''.format('\n'.join(doc)))
        if os.path.isdir(self._name):
            shutil.rmtree(self._name)
        os.makedirs(self._name)
        for n, foot in footprints:
            with open('%s/%s.kicad_mod' % (self._name, n), 'w') as f:
                f.write(foot)
        
class Device(object):
    def __init__(self, schematic=None, footprints=[]):
        self.schematic = schematic
        self.footprints = footprints
