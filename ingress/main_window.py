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
        self._treeview.get_selection().connect("changed", self.on_tree_selection_changed)

    def create_notebook(self):
        self._notebook = Gtk.Notebook()
        self._notebook.set_tab_pos(Gtk.PositionType.TOP)
        return self._notebook

    def on_tree_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter != None:
            # remove all pages
            for page in self._notebook.get_children():
                self._notebook.remove(page)

            self.create_general_tab(model[treeiter][1])
            self.create_permissions_tab(model[treeiter][1])
            self._notebook.show_all()

    def create_general_tab(self, filepath):
        # General Page
        grid = Gtk.Grid(row_spacing=2, column_spacing=2, column_homogeneous=True)
        grid.set_name('GeneralTab')
        self._notebook.append_page(grid, Gtk.Label(label="General"))

        filestat = Util.get_file_stat(filepath)

        # if dir then Ask user to calculate
        filesize = str(Util.get_filesize_format(filestat.st_size))
        if os.path.isdir(filepath):
            filesize = "Calculate"

        # Create labels for general tab
        filename_label = Util.create_label("Name:")
        filename = Util.create_label(os.path.basename(filepath))
        filesize_label = Util.create_label("Filesize:")
        filesize = Gtk.Button(label=filesize)
        location_label = Util.create_label("Location:")
        location = Util.create_label(os.path.dirname(filepath))
        last_modified_label = Util.create_label("Last Modified:")
        last_modified = Util.create_label(time.ctime(filestat.st_mtime))
        last_access_label = Util.create_label("Last Access:")
        last_access = Util.create_label(time.ctime(filestat.st_atime))

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

    def create_permissions_tab(self, filepath):
        # Permissions Page
        grid = Gtk.Grid(row_spacing=2, column_spacing=2, column_homogeneous=True)
        grid.set_name('PermissionsGrid')
        self._notebook.append_page(grid, Gtk.Label(label="Permissions"))

        # stat the file
        filestat = Util.get_file_stat(filepath)
        owner_name = Util.get_usrname_from_uid(filestat.st_uid).pw_name
        group_name = Util.get_grpname_from_gid(filestat.st_gid).gr_name

        # Owner
        owner_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 5)
        owner_label = Util.create_label("Owner:")
        owner = Util.create_label(owner_name)
        owner_box.pack_start(owner_label, False, True, 0)
        owner_box.pack_start(owner, False, True, 20)
        grid.add(owner_box)

        # Group
        grp_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 5)
        group_label = Util.create_label("Group:")
        group = Util.create_label(group_name)
        grp_box.pack_start(group_label, False, True, 0)
        grp_box.pack_start(group, False, True, 22)
        grid.attach(grp_box, 0, 1, 2, 1)

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
