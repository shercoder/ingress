#!/usr/bin/python3

from gi.repository import Gtk
from  model_view import *

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
LEFT_PANED_WIDTH = 300

class IngressMainWindow(Gtk.Window):
    def __init__(self):
        super(IngressMainWindow, self).__init__(type=Gtk.WindowType.TOPLEVEL, title="Ingress")

        Gtk.Window.set_size_request(self, WINDOW_WIDTH, WINDOW_HEIGHT)
        Gtk.Window.set_position(self, Gtk.WindowPosition.CENTER_ALWAYS)

        #window paned
        self.paned_widget = self.add_paned()

        self.display_selected_file_info()

    def add_paned(self):
        paned = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        paned.pack2(Gtk.Frame())

        self.create_tree()
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_border_width(10)
        scrolled_window.set_policy(Gtk.PolicyType.ALWAYS, Gtk.PolicyType.ALWAYS)
        scrolled_window.add_with_viewport(self.treeview)
        paned.pack1(scrolled_window, shrink=False)

        Gtk.Widget.set_size_request(paned.get_child1(), LEFT_PANED_WIDTH, -1)

        self.add(paned)
        return paned

    def create_tree(self):
        self.store = IngressTreeStore()
        self.treeview = IngressTreeView(self.store)

    def display_selected_file_info(self):
        selection = self.treeview.get_selection()
        selection.connect("changed", self.on_tree_selection_changed)
        # print(selection.get_user_data())

    def on_tree_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter != None:
            print("You selected", model[treeiter][1])

    def quit_main_window(self):
        self.connect("delete-event", Gtk.main_quit)

def main():
    win = IngressMainWindow()
    win.quit_main_window()
    win.show_all()
    Gtk.main()

if __name__ == '__main__':
    main()
