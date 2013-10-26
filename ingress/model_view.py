#!/usr/bin/python3

from gi.repository import Gtk
from os.path import expanduser
import os

HOME = expanduser("~")

class IngressTreeStore(Gtk.TreeStore):
    def __init__(self):
        super(IngressTreeStore, self).__init__(str, str)
        self.generate_tree(HOME)


    def generate_tree(self, path, parent=None):
        if parent is None:
            parent = self.append(parent, [os.path.basename(path), path])
            self.append(parent, None)
        else:
            self.remove(self.iter_children(parent))
            for filename in sorted(os.listdir(path)):
                fullpath = os.path.join(path, filename)

                if filename.startswith('.'): continue
                if os.path.isdir(fullpath):
                    child_parent = self.append(parent, [filename, fullpath])
                    self.append(child_parent, None)
                else:
                    self.append(parent, [filename, fullpath])

class IngressTreeView(Gtk.TreeView):
    def __init__(self, treestore):
        super(IngressTreeView, self).__init__(treestore)
        self.set_name('IngressTreeView')
        self.set_headers_visible(False)

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(None, renderer, text=0)
        self.append_column(column)
        self.connect("test-expand-row", self.on_row_expanded)
        self.connect("row-collapsed", self.on_row_collapsed)

    def on_row_expanded(self, view, iter, treepath):
        model = self.get_model()
        fullpath = model[iter][1]
        model.generate_tree(fullpath, iter)

    def on_row_collapsed(self, view, iter, path):
        model = self.get_model()
        if model.iter_has_child(iter):
            while model.iter_has_child(iter):
                model.remove(model.iter_children(iter))
            model.append(iter, None)
