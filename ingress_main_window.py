#!/usr/bin/python3

from gi.repository import Gtk
from  ingress_model_view import IngressTreeStore
from os.path import expanduser

HOME = expanduser("~")
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
LEFT_PANED_WIDTH = 300

class IngressMainWindow(Gtk.Window):
    """docstring for IngressMainWindow"""
    def __init__(self):
        super(IngressMainWindow, self).__init__(type=Gtk.WindowType.TOPLEVEL, title="Ingress")

        Gtk.Window.set_size_request(self, WINDOW_WIDTH, WINDOW_HEIGHT)
        Gtk.Window.set_position(self, Gtk.WindowPosition.CENTER_ALWAYS)

        #window paned
        self.paned_widget = self.add_paned()

    def add_paned(self):
        paned = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)

        paned.add1(self._add_tree_view())
        paned.add2(Gtk.Button(label="My Button2"))

        Gtk.Widget.set_size_request(paned.get_child1(), LEFT_PANED_WIDTH, WINDOW_HEIGHT)

        self.add(paned)
        return paned

    def _add_tree_view(self):

        store = IngressTreeStore(str)
        store.generate_tree(HOME)

        treeview = Gtk.TreeView(store)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("FileName", renderer, text=0)
        treeview.append_column(column)
        return treeview

    def quit_main_window(self):
        self.connect("delete-event", Gtk.main_quit)

def main():
    win = IngressMainWindow()
    win.quit_main_window()
    win.show_all()
    Gtk.main()

if __name__ == '__main__':
    main()