#!/usr/bin/python3

from gi.repository import Gtk
import os

class IngressTreeStore(Gtk.TreeStore):
    def __init__(self, *arg):
        super(IngressTreeStore, self).__init__(*arg)

    def generate_tree(self, path):
        parents = {}
        parents[path] = self.append(None, [os.path.basename(path)])
        for dirname, subdirs, files in sorted(os.walk(path)):
            for subdir in subdirs:
                parents[os.path.join(dirname, subdir)] = self.append(parents.get(dirname, None), [subdir])

            for file in sorted(files):
               self.append(parents.get(dirname, None), [file])
