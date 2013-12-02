from pygit2 import Repository as _Repository
from pygit2 import *
from gi.repository import Gtk, Gdk

class Repository(_Repository):
    def __init__(self, repopath):
        super(Repository, self).__init__(repopath)

    def get_cur_branch(self):
        for b in self.branches():
            branch = self.lookup_branch(b)
            if branch.is_head(): return branch.branch_name

    def branches(self):
        return self.listall_branches()

    def branch_list_store(self):
        list_store = Gtk.ListStore(str)
        for branch in self.branches():
            list_store.append([branch])
        return list_store

    def get_status_current(self):
        status = self.status()
        files = list()
        for filepath, flags in status.items():
            if flags == GIT_STATUS_CURRENT:
                files.append(filepath)
        return files

    def get_status_ignored(self):
        status = self.status()
        files = list()
        for filepath, flags in status.items():
            if flags == GIT_STATUS_IGNORED:
                files.append(filepath)
        return files

    def get_status_wt(self):
        status = self.status()
        files = dict()
        for filepath, flags in status.items():
            if flags == GIT_STATUS_WT_DELETED or \
                flags == GIT_STATUS_WT_MODIFIED or \
                flags == GIT_STATUS_WT_NEW:
                files[filepath] = flags
        return files

    def get_status_index(self):
        status = self.status()
        files = dict()
        for filepath, flags in status.items():
            if flags == GIT_STATUS_INDEX_DELETED or \
                flags == GIT_STATUS_INDEX_MODIFIED or \
                flags == GIT_STATUS_INDEX_NEW:
                files[filepath] = flags
        return files

    def commit_count(self):
        return sum(1 for _ in self.walk(self.head.target, GIT_SORT_TOPOLOGICAL))


class CreateBranchDialog(Gtk.Window):
    def __init__(self, window, repo):
        Gtk.Window.__init__(self, title="Compress")
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self.set_transient_for(window)
        self.build_dialog(repo)


    def build_dialog(self, repo):
        content_grid = Gtk.Grid()
        content_grid.set_margin_left(12)
        content_grid.set_margin_right(12)
        content_grid.set_margin_top(12)
        content_grid.set_margin_bottom(12)
        content_grid.set_row_spacing(6)
        content_grid.set_column_spacing(12)

        entry = Gtk.Entry()
        force_chk = Gtk.CheckButton(label="Force")

        # create button box
        buttonbox = Gtk.ButtonBox(Gtk.Orientation.HORIZONTAL)
        buttonbox.set_layout(Gtk.ButtonBoxStyle.END)
        cancel_button = Gtk.Button.new_from_stock(Gtk.STOCK_CANCEL)
        create_button = Gtk.Button.new_with_label("Create")
        create_button.set_sensitive(False)
        buttonbox.pack_end(cancel_button, False, False, 0)
        buttonbox.pack_end(create_button, False, False, 0)

        entry.connect("changed", self.on_entry_changed, create_button)
        cancel_button.connect("clicked", self.on_cancel_clicked)
        create_button.connect("clicked", self.on_create_clicked, entry, force_chk, repo)

        content_grid.attach(entry, 0, 0, 1, 1)
        content_grid.attach(force_chk, 1, 0, 1, 1)
        content_grid.attach(buttonbox, 0, 1, 1, 1)
        self.add(content_grid)
        self.show_all()

    def on_cancel_clicked(self, button):
        self.destroy()

    def on_create_clicked(self, button, entry, force, repo):
        branch_name = entry.get_text().strip()
        if branch_name:
            try:
                repo.create_branch(branch_name, repo.head.get_object(), force.get_active())
            except Exception as e:
                print(e)
            self.destroy()

    def on_entry_changed(self, entry, create_button):
        if entry.get_text().strip():
            create_button.set_sensitive(True)
        else:
            create_button.set_sensitive(False)
