#!/usr/bin/python3

from gi.repository import Gtk
import os

class IngressTreeStore(Gtk.TreeStore):
    def __init__(self):
        super(IngressTreeStore, self).__init__(str, str)

    def generate_tree(self, path):
        parents = {}
        parents[path] = self.append(None, [os.path.basename(path), path])
        for dirname, subdirs, files in sorted(os.walk(path)):
            for subdir in subdirs:
                parents[os.path.join(dirname, subdir)] = self.append(parents.get(dirname, None), [subdir, os.path.join(dirname, subdir)])

            for file in sorted(files):
               self.append(parents.get(dirname, None), [file, os.path.join(dirname, file)])

class IngressFileBasicInfo(object):
    def __init__(self, fullpath, type):
        self.fullpath = fullpath
        self.type = type
