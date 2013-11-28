#!/usr/bin/python3

from gi.repository import Gtk, Gdk
from  model_view import *
from ingress_css import *
from constants import *
from util import Util
from tagfs import *
import time
from git_repo import *
import pygit2
import fnmatch

class IngressMainWindow(Gtk.Window):
    TARGETS = [
        ('INGRESS_TREE_MODEL_ROW', Gtk.TargetFlags.SAME_WIDGET|Gtk.TargetFlags.OTHER_WIDGET, 0)
    ]

    def __init__(self):
        super(IngressMainWindow, self).__init__(type=Gtk.WindowType.TOPLEVEL, title="Ingress")
        self.set_size_request(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_border_width(6)
        self.set_icon_name('ingress')
        self.set_icon_from_file('system_file_manager.png')

        # Vertical box
        self._window_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        self.add(self._window_vbox)

        # Toolbar
        self.add_toolbar()

        # Show Hidden Checkbox
        self.add_show_hidden_chkbox()

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

        # creating index manager
        self._index_manager = IndexManager()

    def quit_main_window(self):
        self.connect("delete-event", Gtk.main_quit)

    def add_paned(self):
        self._paned = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)

        self.create_tree()
        scrolled_window_left = Gtk.ScrolledWindow()
        scrolled_window_left.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window_left.add(self._treeview)
        self._paned.pack1(scrolled_window_left, shrink=False)
        Gtk.Widget.set_size_request(self._paned.get_child1(), LEFT_PANED_WIDTH, -1)

        # pack 2
        scrolled_window_right = Gtk.ScrolledWindow()
        scrolled_window_right.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window_right.add_with_viewport(self.create_notebook())
        self._paned.pack2(scrolled_window_right, shrink=False)
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
        self._search_bar.connect("activate", self.on_search_enter_key)
        toolitem.add(self._search_bar)
        self._toolbar.insert(toolitem, -1)

    def add_show_hidden_chkbox(self):
        toolitem = Gtk.ToolItem()
        self._show_hidden_chkbox = Gtk.CheckButton(label="Show Hidden Files")
        toolitem.add(self._show_hidden_chkbox)
        self._toolbar.insert(toolitem, -1)
        self._show_hidden_chkbox.connect("toggled", self.on_show_hidden_chkbox, "Show Hidden")

    def create_tree(self):
        self._store = IngressTreeStore()
        self._treeview = IngressTreeView(self._store, self)
        self._treeview.set_enable_tree_lines(True)
        self._treeview.get_selection().connect("changed", self.on_tree_selection_changed)

        # drag and drop setting
        self._treeview.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK,
                                                                self.TARGETS,
                                                                Gdk.DragAction.DEFAULT | Gdk.DragAction.MOVE)
        self._treeview.enable_model_drag_dest(self.TARGETS, Gdk.DragAction.DEFAULT)

        self._treeview.drag_dest_add_text_targets()
        self._treeview.drag_source_add_text_targets()

        self._treeview.connect("drag_data_get", self._dnd_get_data)
        self._treeview.connect("drag_data_received", self._dnd_data_received)

    def create_notebook(self):
        self._notebook = Gtk.Notebook()
        self._notebook.set_tab_pos(Gtk.PositionType.TOP)
        return self._notebook

    def create_general_tab(self, filepath):
        # General Page
        grid = Gtk.Grid(row_spacing=2, column_spacing=10)
        grid.set_name('GeneralTab')
        self._notebook.append_page(grid, Gtk.Label(label="General"))

        filestat = Util.get_file_stat(filepath)

        # if dir then Ask user to calculate
        size_of_file = str(Util.get_filesize_format(filestat.st_size))
        if os.path.isdir(filepath):
            filesize = Gtk.Button(label="Calculate")
            filesize.connect("clicked", self.on_clicked_filesize_button)
            filesize.set_tooltip_text("Click to calculate")
        else:
            filesize = Util.create_info_label(size_of_file)
        filesize.set_size_request(70, 30)

        # Create labels for general tab
        filename_label = Util.create_label("Name:")
        filename = Util.create_info_label(os.path.basename(filepath))
        filesize_label = Util.create_label("Filesize:")

        # filesize = Gtk.Button(label=filesize)

        location_label = Util.create_label("Location:")
        location = Util.create_info_label(os.path.dirname(filepath))
        last_modified_label = Util.create_label("Last Modified:")
        last_modified = Util.create_info_label(time.ctime(filestat.st_mtime))
        last_access_label = Util.create_label("Last Access:")
        last_access = Util.create_info_label(time.ctime(filestat.st_atime))

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

        # Add tags to file
        if not os.path.isdir(filepath):
            self.add_tagging_to_grid(filepath, grid)

    def add_tagging_to_grid(self, filepath, grid):
        # Add separator
        hseparator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        grid.attach(hseparator, 0, 5, 3, 3)

        # Add tags
        tagging_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        tag_entry = Gtk.Entry()
        add_tag_button = Gtk.Button(label="Add Tag")
        add_tag_button.connect("clicked", self.on_clicked_add_tag, (filepath, tag_entry))
        tagging_box.pack_start(tag_entry, False, False, True)
        tagging_box.pack_start(add_tag_button, False, False, True)
        grid.attach(tagging_box, 0, 10, 3, 3)

        tags = self._index_manager.get_tags_for_filepath(filepath)
        if tags:
            tags_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
            tags = tags = str(tags).split(' ')
            row = 14
            for i, tag in enumerate(tags):
                if i%5 == 0:
                    grid.attach(tags_box, 0, row, 1, 1)
                    tags_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
                    row += 1
                tag_label = TagLabel(tag)
                tag_label.connect("close-clicked", self.on_tag_label_close_clicked, filepath, tags_box)
                tags_box.pack_start(tag_label, False, False, True)
            grid.attach(tags_box, 0, row, 1, 1)


    def generate_git_info(self, grid, filepath):
        repo = Repository(filepath)

        git_label = Util.create_label("<big><u>Git Repository Information</u></big>")
        git_label.set_use_markup(True)
        grid.attach(git_label, 0, 10, 1, 1)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        # Current branch name
        cur_branch_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        cur_branch_label = Util.create_label("Current Branch: ")
        cur_branch_name = Util.create_info_label(repo.get_cur_branch())
        cur_branch_hbox.pack_start(cur_branch_label, False, False, 1)
        cur_branch_hbox.pack_start(cur_branch_name, False, False, 1)
        vbox.pack_start(cur_branch_hbox, False, False, 1)

        # branch list combo box
        branch_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        branches_label = Util.create_label("All Branches: ")
        branch_hbox.pack_start(branches_label, False, False, 1)
        branch_combo = Gtk.ComboBox.new_with_model(repo.branch_list_store())
        renderer_text = Gtk.CellRendererText()
        branch_combo.pack_start(renderer_text, True)
        branch_combo.add_attribute(renderer_text, "text", 0)
        branch_hbox.pack_start(branch_combo, False, False, 1)
        vbox.pack_start(branch_hbox, False, False, 1)

        # total commits
        count_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        count_label = Util.create_label("Total Commits:")
        count_hbox.pack_start(count_label, False, False, 1)
        count_entry = Gtk.Entry()
        count_entry. set_max_length(4)
        count_entry.set_width_chars(4)
        count_entry.set_text(str(repo.commit_count()))
        count_entry.set_editable(False)
        count_hbox.pack_start(count_entry, False, False, 1)
        vbox.pack_start(count_hbox, False, False, 1)

        # status button
        status_btn = Gtk.Button(label="Git Status")
        status_btn.connect("clicked", self.create_git_status_tab, repo)
        vbox.pack_start(status_btn, False, False, 1)

        # add vbox to the grid
        grid.attach(vbox, 0, 12, 1, 1)

    ################Callbacks #####################

    def on_tree_selection_changed(self, selection):
        if selection.count_selected_rows() == 1:
            model, treepath = selection.get_selected_rows()
            treeiter = model.get_iter(treepath[0])
            if treeiter != None:
                # remove all pages
                for page in self._notebook.get_children():
                    self._notebook.remove(page)

                self.create_general_tab(model[treeiter][1])
                self.create_permissions_tab(model[treeiter][1])
                self._notebook.show_all()

    def on_show_hidden_chkbox(self, button, name):
        self._treeview.get_model().set_show_hidden(button.get_active())

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

        # wt_label = Util.create_label("<big>Git Status</big>")
        # vbox.pack_start(wt_label, False, False, 1)

        # Display WT info
        wt_status_code = {
            pygit2.GIT_STATUS_WT_NEW: "new:",
            pygit2.GIT_STATUS_WT_MODIFIED: "modified:",
            pygit2.GIT_STATUS_WT_DELETED: "deleted:"
        }

        index_status_code = {
            pygit2.GIT_STATUS_INDEX_NEW: "new:",
            pygit2.GIT_STATUS_INDEX_MODIFIED: "modified:",
            pygit2.GIT_STATUS_INDEX_DELETED: "deleted:"
        }

        # working dir
        store = Gtk.ListStore(str, str)
        files = repo.get_status_wt()
        for filename in files:
            store.append([wt_status_code[files[filename]], filename])

        tree = Gtk.TreeView(store)
        column = Gtk.TreeViewColumn("Working Directory")
        filename = Gtk.CellRendererText()
        file_status = Gtk.CellRendererText()
        column.pack_start(file_status, True)
        column.pack_start(filename, True)
        column.add_attribute(file_status, "text", 0)
        column.add_attribute(filename, "text", 1)
        tree.append_column(column)

        vbox.pack_start(tree, False, False, 5)

        # Index
        store = Gtk.ListStore(str, str)
        files = repo.get_status_index()
        for filename in files:
            store.append([index_status_code[files[filename]], filename])

        tree = Gtk.TreeView(store)
        column = Gtk.TreeViewColumn("Index Directory")
        filename = Gtk.CellRendererText()
        file_status = Gtk.CellRendererText()
        column.pack_start(file_status, True)
        column.pack_start(filename, True)
        column.add_attribute(file_status, "text", 0)
        column.add_attribute(filename, "text", 1)
        tree.append_column(column)

        vbox.pack_start(tree, False, False, 5)

        self._notebook.append_page(vbox, Gtk.Label("Git Status"))
        self._notebook.show_all()

    def on_search_enter_key(self, entry):
        # find /home/shercoder/ \( ! -regex '.*/\..*' \) | grep "soccer"
        search_terms = entry.get_text()
        is_tag_search = False
        if search_terms.startswith('@'):
            search_terms = search_terms[1:]
            is_tag_search = True
        else:
            search_terms = search_terms.split(' ')

        if entry.get_text():
            allfiles = []
            if is_tag_search:
                results = self._index_manager.search_documents(search_terms)
                for hit in results:
                    allfiles.append((hit['filename'], hit['filepath']))
            else:
                for root, dirs, files in os.walk(HOME):
                    files = [f for f in files if not f[0] == '.']
                    dirs[:] = [d for d in dirs if not d[0] == '.']
                    for term in search_terms:
                        for filename in fnmatch.filter(files, "*{}*".format(term)):
                            allfiles.append((filename, os.path.join(root, filename)))
            self._treeview.get_model().generate_search_tree(allfiles)
        else:
            self._treeview.get_model().generate_tree(HOME)
            Util.clear_notebook(self._notebook)

    def on_clicked_add_tag(self, button, user_data):
        filepath, entry = user_data
        tags = entry.get_text()
        self._index_manager.update_document(filepath, tags)
        self._notebook.show_all()

    def on_tag_label_close_clicked(self, tag_label, filepath, box):
        self._index_manager.delete_tag(filepath, tag_label.label.get_text())
        tag_label.destroy()
        box.show_all()

    # drag and drop callbacks
    def _dnd_get_data(self, treeview, context, selection, targetType, eventTime):
        treeselection = treeview.get_selection()
        model, treepaths = treeselection.get_selected_rows()

        # get the first iter, don't allow multiple selection drag n drop
        iterator = model.get_iter(treepaths[0])
        data = model.get_value(iterator, 1)
        selection.set(selection.get_target(), 8, data)

    def _dnd_data_received(self, treeview, context, x, y, selection, targetType, time):
        model = treeview.get_model()
        data = selection.get_data()
        drop_info = treeview.get_dest_row_at_pos(x, y)
        if drop_info:
            path, position = drop_info
            iterator = model.get_iter(path)
            if not os.path.isdir(model[iterator][1]):
                iterator = model.iter_parent(iterator)
            dest_path = model[iterator][1]

            # Only move on valid move
            if self.can_move_file(data, dest_path):
                new_filepath = os.path.join(dest_path, os.path.basename(data))
                if os.path.exists(new_filepath):
                    # Ask user to overwrite or rename new file
                    if self.overwrite_file_dialog():
                        model.append(iterator, [os.path.basename(data), new_filepath])
                        Util.cp_file(data, new_filepath)
                    else:
                        text = self.rename_file_dialog()
                        if text is not None and not os.path.exists(os.path.join(dest_path, text)):
                            new_filepath = os.path.join(dest_path, text)
                            model.append(iterator, [text, new_filepath])
                            Util.cp_file(data, new_filepath)
                else:
                    new_filepath = os.path.join(dest_path, os.path.basename(data))
                    model.append(iterator, [os.path.basename(data), new_filepath])
                    Util.cp_file(data, new_filepath)

                # update treeview
                treepath = model.get_path(iterator)
                self._treeview.collapse_row(treepath)
                self._treeview.expand_to_path(treepath)

        if Gdk.DragAction.MOVE == context.get_actions():
            context.finish(True, True, etime)
        return

    # Drag and Drop Utility functions
    def can_move_file(self, src, dest):
        if src == dest: return False                                # if both paths are same
        if os.path.dirname(src) == dest: return False   # if from and to locations are same (same dir)
        # TODO: check if user has the write permissions to move
        return True

    def overwrite_file_dialog(self):
        dialog = Gtk.MessageDialog(self, Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.QUESTION,
            Gtk.ButtonsType.YES_NO, "File already exists!")
        dialog.format_secondary_text("Would you like to overwrite existing file?")
        dialog.set_title("Rename")

        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.YES:
            return True
        elif response == Gtk.ResponseType.NO:
            return False

    def rename_file_dialog(self):
        dialog = Gtk.MessageDialog(self, Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.QUESTION,
            Gtk.ButtonsType.OK_CANCEL, "Would you like to rename new file before moving?")
        dialog.set_title("Rename")

        box = dialog.get_content_area()
        userEntry = Gtk.Entry()
        userEntry.set_size_request(150,0)
        box.pack_end(userEntry, False, False, 0)
        dialog.show_all()

        response = dialog.run()
        text = userEntry.get_text()
        dialog.destroy()
        if response == Gtk.ResponseType.OK and (text != ''):
            return text
        elif response == Gtk.ResponseType.CANCEL:
            return None

def main():
    win = IngressMainWindow()
    win.quit_main_window()
    win.show_all()
    Gtk.main()

if __name__ == '__main__':
    main()
