#!/usr/bin/python3

from gi.repository import Gtk, Gdk
from  model_view import *
from ingress_css import *
from util import Util
import time

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 500
LEFT_PANED_WIDTH = 300

class IngressMainWindow(Gtk.Window):
    def __init__(self):
        super(IngressMainWindow, self).__init__(type=Gtk.WindowType.TOPLEVEL, title="Ingress")
        self.set_size_request(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_border_width(6)
        self.set_icon_name('ingress')

        #window paned
        self.add_paned()
        self.display_selected_file_info()

        # set css provider
        self._style_provider = Gtk.CssProvider()
        self._style_provider.load_from_data(ingress_css)
        self.get_style_context().add_provider_for_screen(
            Gdk.Screen.get_default(),
            self._style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def quit_main_window(self):
        self.connect("delete-event", Gtk.main_quit)

    def add_paned(self):
        self._paned = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)

        self.create_tree()
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.add(self._treeview)
        self._paned.pack1(scrolled_window, shrink=False)
        Gtk.Widget.set_size_request(self._paned.get_child1(), LEFT_PANED_WIDTH, -1)

        # pack 2
        self._paned.pack2(self.create_notebook())

        self.add(self._paned)

    def create_tree(self):
        self._store = IngressTreeStore()
        self._treeview = IngressTreeView(self._store)
        self._treeview.set_enable_tree_lines(True)

    def create_notebook(self):
        self._notebook = Gtk.Notebook()
        self._notebook.set_tab_pos(Gtk.PositionType.TOP)
        self.create_general_tab()
        self.create_permissions_tab()
        return self._notebook

    def display_selected_file_info(self):
        selection = self._treeview.get_selection()
        selection.connect("changed", self.on_tree_selection_changed)

    def on_tree_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter != None:
            self.update_general_tab(model[treeiter][1])
            self.update_permissions_tab(model[treeiter][1])

    def update_general_tab(self, filepath):
        grid = self._notebook.get_nth_page(0)

        filestat = Util.get_file_stat(filepath)
        grid.get_children()[0].set_text(time.ctime(filestat.st_atime))
        grid.get_children()[2].set_text(time.ctime(filestat.st_mtime))
        grid.get_children()[4].set_text(os.path.dirname(filepath))

        # if dir then Ask user to calculate
        filesize = str(Util.get_filesize_format(filestat.st_size))
        if os.path.isdir(filepath):
            filesize = "Calculate"

        grid.get_children()[6].set_label(filesize)
        grid.get_children()[8].set_text(os.path.basename(filepath))

    def update_permissions_tab(self, filepath):
        grid = self._notebook.get_nth_page(1)
        filestat = Util.get_file_stat(filepath)
        owner = Util.get_usrname_from_uid(filestat.st_uid)
        group = Util.get_grpname_from_gid(filestat.st_gid)

        grid.get_children()[0].set_text(group.gr_name)
        grid.get_children()[2].set_text(owner.pw_name)
        # self._notebook.next_page()

    def create_general_tab(self):
        # General Page
        grid = Gtk.Grid(row_spacing=2, column_spacing=2, column_homogeneous=True)
        grid.set_name('GeneralTab')
        self._notebook.append_page(grid, Gtk.Label(label="General"))

        # Create labels for general tab
        filename_label = Util.create_label("Name:")
        filename = Util.create_label("shercoder")
        filesize_label = Util.create_label("Filesize:")
        filesize = Gtk.Button(label="Calculate")
        location_label = Util.create_label("Location:")
        location = Util.create_label("location goes here")
        last_modified_label = Util.create_label("Last Modified:")
        last_modified = Util.create_label("last modified goes here")
        last_access_label = Util.create_label("Last Access:")
        last_access = Util.create_label("last access goes here")

        filesize.connect("clicked", self.on_clicked_filesize_button)

        # Add label locations
        grid.attach(filename_label, 0, 0, 1, 1)
        grid.attach(filename, 1, 0, 1, 1)
        grid.attach(filesize_label, 0, 1, 1, 1)
        grid.attach(filesize, 1, 1, 1, 1)
        grid.attach(location_label, 0, 2, 1, 1)
        grid.attach(location, 1, 2, 1, 1)
        grid.attach(last_modified_label, 0, 3, 1, 1)
        grid.attach(last_modified, 1, 3, 1, 1)
        grid.attach(last_access_label, 0, 4, 1, 1)
        grid.attach(last_access, 1, 4, 1, 1)

    def create_permissions_tab(self):
        # Permissions Page
        grid = Gtk.Grid(row_spacing=2, column_spacing=2, column_homogeneous=True)
        grid.set_name('PermissionsGrid')
        self._notebook.append_page(grid, Gtk.Label(label="Permissions"))

        # Owner
        owner_label = Util.create_label("Owner:")
        owner = Util.create_label("Owner??")
        grid.add(owner_label)
        grid.attach(owner, 1, 0, 1, 1)

        # Group
        grp_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 5)
        group_label = Util.create_label("Group:")
        group = Util.create_label("Group??")
        grp_box.pack_start(group_label, False, True, 0)
        grp_box.pack_start(group, False, True, 20)
        grid.attach(grp_box, 0, 1, 2, 1)
        # grid.attach(group_label, 0, 1, 1, 1)
        # grid.attach(group, 1, 1, 1, 1)

    def on_clicked_filesize_button(self, button):
        (model, sel_iter) = self._treeview.get_selection().get_selected()
        if os.path.isdir(model[sel_iter][1]):
            filesize = Util.get_dir_size(model[sel_iter][1])
            button.set_label(Util.get_filesize_format(filesize))

def main():
    win = IngressMainWindow()
    win.quit_main_window()
    win.show_all()
    Gtk.main()

if __name__ == '__main__':
    main()
