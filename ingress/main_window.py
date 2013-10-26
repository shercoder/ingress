#!/usr/bin/python3

from gi.repository import Gtk, Gdk
from  model_view import *
from ingress_css import *
from util import Util
import time
from git_repo import *
import pygit2

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

        # Vertical box
        self._window_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        self.add(self._window_vbox)

        # Toolbar
        self.add_toolbar()

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
        self._window_vbox.pack_start(self._paned, True, True, True)

    def add_toolbar(self):
        self._toolbar = Gtk.Toolbar()
        self._toolbar.set_style(Gtk.ToolbarStyle.BOTH)
        self._toolbar.set_border_width(2)
        self._window_vbox.pack_start(self._toolbar, False, False, True)

        # add tool items
        self.add_search_tool()

    def add_search_tool(self):
        toolitem = Gtk.ToolItem()
        self._search_bar = Gtk.Entry()
        toolitem.add(self._search_bar)
        self._toolbar.insert(toolitem, -1)

    def create_tree(self):
        self._store = IngressTreeStore()
        self._treeview = IngressTreeView(self._store)
        self._treeview.set_enable_tree_lines(True)
        self._treeview.get_selection().connect("changed", self.on_tree_selection_changed)

    def create_notebook(self):
        self._notebook = Gtk.Notebook()
        self._notebook.set_tab_pos(Gtk.PositionType.TOP)
        return self._notebook

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
        filename = Util.create_info_label(os.path.basename(filepath))
        filesize_label = Util.create_label("Filesize:")
        filesize = Gtk.Button(label=filesize)
        location_label = Util.create_label("Location:")
        location = Util.create_info_label(os.path.dirname(filepath))
        last_modified_label = Util.create_label("Last Modified:")
        last_modified = Util.create_info_label(time.ctime(filestat.st_mtime))
        last_access_label = Util.create_label("Last Access:")
        last_access = Util.create_info_label(time.ctime(filestat.st_atime))

        filesize.connect("clicked", self.on_clicked_filesize_button)
        filesize.set_tooltip_text("Click to calculate")
        # filesize.set_size_request(filesize.get_allocation().width-.5, -1)

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

        # Add separator
        hseparator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        grid.attach(hseparator, 0, 5, 3, 3)

        # Git Info
        if os.path.isdir(filepath) and Util.has_git_repo(filepath):
            self.generate_git_info(grid, filepath)

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
        owner_box.set_homogeneous(True)
        owner_label = Util.create_label("Owner:")
        owner = Util.create_info_label(owner_name)
        owner_box.pack_start(owner_label, False, False, True)
        owner_box.pack_start(owner, False, False, True)
        grid.add(owner_box)

        # Group
        grp_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 5)
        grp_box.set_homogeneous(True)
        group_label = Util.create_label("Group:")
        group = Util.create_info_label(group_name)
        grp_box.pack_start(group_label, False, False, True)
        grp_box.pack_start(group, False, False, True)
        grid.attach(grp_box, 0, 1, 1, 1)

        # Permission Mode
        perm_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 5)
        grp_box.set_homogeneous(True)
        perms = Util.create_info_label(Util.create_perm_str(filestat.st_mode))

        # Entry box
        perms_entry = Gtk.Entry.new()
        perms_entry.set_max_length(3)
        perms_entry.set_width_chars(3)
        perms_entry.set_text(Util.create_777_format(filestat.st_mode))
        perms_entry.connect("changed", self.on_perms_changed, perms)

        # pack perm label and entry together
        perm_box.pack_start(perms, False, True, 0)
        perm_box.pack_start(perms_entry, False, True, 0)
        grid.attach(perm_box, 0, 2, 3, 1)

    def generate_git_info(self, grid, filepath):
        repo = Repository(filepath)

        git_label = Util.create_label("<big><b><u>Git Repository Information</u></b></big>")
        git_label.set_use_markup(True)
        grid.attach(git_label, 0, 10, 1, 1)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        # branch list combo box
        branch_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        branches_label = Util.create_label("All Branches: ")
        branch_hbox.pack_start(branches_label, False, False, True)
        branch_combo = Gtk.ComboBox.new_with_model(repo.branch_list_store())
        renderer_text = Gtk.CellRendererText()
        branch_combo.pack_start(renderer_text, True)
        branch_combo.add_attribute(renderer_text, "text", 0)
        branch_hbox.pack_start(branch_combo, False, False, True)
        vbox.pack_start(branch_hbox, False, False, True)

        # total commits
        count_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        count_label = Util.create_label("Total Commits:")
        count_hbox.pack_start(count_label, False, False, True)
        count_entry = Gtk.Entry()
        count_entry. set_max_length(4)
        count_entry.set_width_chars(4)
        count_entry.set_text(str(repo.commit_count()))
        count_entry.set_editable(False)
        count_hbox.pack_start(count_entry, False, False, True)
        vbox.pack_start(count_hbox, False, False, True)

        # status button
        status_btn = Gtk.Button(label="Git Status")
        status_btn.connect("clicked", self.create_git_status_tab, repo)
        vbox.pack_start(status_btn, False, False, True)

        # add vbox to the grid
        grid.attach(vbox, 0, 12, 1, 1)

    ################Callbacks #####################

    def on_tree_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter != None:
            # remove all pages
            for page in self._notebook.get_children():
                self._notebook.remove(page)

            self.create_general_tab(model[treeiter][1])
            self.create_permissions_tab(model[treeiter][1])
            self._notebook.show_all()

    def on_clicked_filesize_button(self, button):
        (model, sel_iter) = self._treeview.get_selection().get_selected()
        if os.path.isdir(model[sel_iter][1]):
            filesize = Util.get_dir_size(model[sel_iter][1])
            button.set_label(Util.get_filesize_format(filesize))

    def on_perms_changed(self, entry, perms_label):
        text = entry.get_text()
        if len(text) == 3 and Util.is_integer(text):
            (model, treeiter) = self._treeview.get_selection().get_selected()
            os.chmod(model[treeiter][1], int(text, 8))
            filestat = Util.get_file_stat(model[treeiter][1])
            perms_label.set_label(Util.create_perm_str(filestat.st_mode))

    def create_git_status_tab(self, button, repo):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        wt_label = Util.create_label("<big>Working Dir Status</big>")
        vbox.pack_start(wt_label, False, False, True)

        # Display WT info
        wt_status_code = {
            pygit2.GIT_STATUS_WT_NEW: "new:",
            pygit2.GIT_STATUS_WT_MODIFIED: "modified:",
            pygit2.GIT_STATUS_WT_DELETED: "deleted:"
        }
        store = Gtk.ListStore(str, str)
        files = repo.get_status_wt()
        for filename in files:
            store.append([wt_status_code[files[filename]], filename])

        tree = Gtk.TreeView(store)
        column = Gtk.TreeViewColumn("Filename and  Status")
        filename = Gtk.CellRendererText()
        file_status = Gtk.CellRendererText()
        column.pack_start(file_status, True)
        column.pack_start(filename, True)
        column.add_attribute(file_status, "text", 0)
        column.add_attribute(filename, "text", 1)
        tree.append_column(column)

        self._notebook.append_page(tree, Gtk.Label("Git Status"))
        self._notebook.show_all()

def main():
    win = IngressMainWindow()
    win.quit_main_window()
    win.show_all()
    Gtk.main()

if __name__ == '__main__':
    main()
