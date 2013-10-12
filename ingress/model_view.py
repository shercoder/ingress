#!/usr/bin/python3

from gi.repository import Gtk
import os

class IngressTreeStore(Gtk.TreeStore):
    def __init__(self):
        super(IngressTreeStore, self).__init__(str, str)


    def generate_tree(self, path, parent=None):
        parent = self.append(parent, [os.path.basename(path), path])
        self.append(parent, None)
        # for dirname, subdirs, files in sorted(os.walk(path)):
        #     for subdir in subdirs:
        #         parents[os.path.join(dirname, subdir)] = self.append(parents.get(dirname, None), [subdir, os.path.join(dirname, subdir)])

        #     for file in sorted(files):
        #        self.append(parents.get(dirname, None), [file, os.path.join(dirname, file)])

class IngressTreeView(Gtk.TreeView):
    def __init__(self, treestore):
        super().__init__(treestore)
        self.set_headers_visible(False)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(None, renderer, text=0)
        self.append_column(column)
        self.connect("row-expanded", self.on_row_expanded)

    def on_row_expanded(self, iter, treepath, user_data):
        print("I am expanded")

class IngressFileBasicInfo(object):
    def __init__(self, fullpath, type):
        self.fullpath = fullpath
        self.type = type
