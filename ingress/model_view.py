#!/usr/bin/python3

from gi.repository import Gtk
from send2trash import send2trash
from constants import *
import os
from util import Util
from compress import CompressDialog

class IngressTreeStore(Gtk.TreeStore):
    def __init__(self, source_path=HOME):
        super(IngressTreeStore, self).__init__(str, str)
        self.generate_tree(source_path)
        self._show_hidden = False


    def generate_tree(self, path, parent=None):
        if parent is None:
            self.clear()
            parent = self.append(parent, [os.path.basename(path), path])
            self.append(parent, None)
        else:
            self.remove(self.iter_children(parent))
            for filename in sorted(os.listdir(path)):
                fullpath = os.path.join(path, filename)

                if not self._show_hidden and filename.startswith('.'): continue
                if os.path.isdir(fullpath):
                    child_parent = self.append(parent, [filename, fullpath])
                    self.append(child_parent, None)
                else:
                    self.append(parent, [filename, fullpath])

    def generate_search_tree(self, files):
        if files:
            self.clear()
            for filename, filepath in files:
                self.append(None, [filename, filepath])

    def set_show_hidden(self, value):
        self._show_hidden = value

    def get_show_hidden(self):
        return self._show_hidden

class IngressTreeView(Gtk.TreeView):
    def __init__(self, treestore, parent_window):
        super(IngressTreeView, self).__init__(treestore)
        self.parent_window = parent_window

        self.set_name('IngressTreeView')
        self.set_headers_visible(False)

        renderer = Gtk.CellRendererText()
        renderer.set_property("editable", True)
        renderer.connect("edited", self.on_filename_edited)
        column = Gtk.TreeViewColumn(None, renderer, text=0)
        self.append_column(column)
        self.connect("test-expand-row", self.on_row_expanded)
        self.connect("row-collapsed", self.on_row_collapsed)

        # create pop up menu on right click
        self.connect("button_press_event",self.on_right_click)

        # set multiple selection
        self.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)

    def add_popup_menu(self, filepath):
        self.popup = Gtk.Menu()
        # self.popup.append(Gtk.MenuItem(label="Cut"))
        # self.popup.append(Gtk.MenuItem(label="Copy"))
        # self.popup.append(Gtk.MenuItem(label="Paste"))
        # self.popup.append(Gtk.MenuItem(label="Rename"))

        # Open files
        if os.path.isfile(filepath):
            open_file_label = Gtk.MenuItem(label="Open file")
            open_file_label.connect("activate", self.on_activate_open_file, filepath)
            self.popup.append(open_file_label)

        # send file to trash
        move2trash = Gtk.MenuItem(label="Move To Trash")
        move2trash.connect("activate", self.on_activate_move_2_trash)
        self.popup.append(move2trash)

        # compress
        compress = CompressionMenuItem(self.parent_window, self, filepath)
        self.popup.append(compress)
        self.popup.show_all()

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

    def on_right_click(self, treeview, event):
        if event.button == 3: # right click
            pthinfo = treeview.get_path_at_pos(event.x, event.y)
            if pthinfo is not None:
                path, col, cellx, celly = pthinfo
                treeview.grab_focus()
                # treeview.set_cursor(path, col, 0)
                iter = self.get_model().get_iter(path)
                self.add_popup_menu(self.get_model()[iter][1])
                self.popup.popup(None, None, None, None, event.button, event.time)
            return True

    def on_activate_move_2_trash(self, widget):
        selection = self.get_selection()
        model, treepaths = selection.get_selected_rows()
        for treepath in treepaths:
            iter = model.get_iter(treepath)
            filepath = model[iter][1]
            parent = model.iter_parent(iter)
            if parent is not None:
                parent_path = model.get_path(parent)
                send2trash(filepath)
                self.collapse_row(parent_path)
                self.expand_to_path(parent_path)

    def on_filename_edited(self, widget, path, text):
        old_path = self.get_model()[path][1]

        # cannot change user's home dir name
        if old_path is not HOME:
            parent_path = os.path.dirname(old_path)
            new_path = os.path.join(parent_path, text)
            if not os.path.exists(new_path):
                self.get_model()[path][0] = text
                self.get_model()[path][1] = new_path
                Util.rename_file(old_path, new_path)

    def on_activate_open_file(self, widget, filepath):
        import subprocess
        if os.sys.platform.startswith('darwin'):
            subprocess.call(('open', filepath))
        elif os.name == 'nt':
            os.startfile(filepath)
        elif os.name == 'posix':
            subprocess.call(('xdg-open', filepath))


class CompressionMenuItem(Gtk.MenuItem):
    def __init__(self, window, treeview, filepath):
        Gtk.MenuItem.__init__(self, label="Compress")
        self._filepath = filepath
        self.parent_window = window
        self.connect("activate", self.on_activate_compress, window, treeview, filepath)

    def on_activate_compress(self, widget, window, treeview, filepath):
        dialog = CompressDialog(window, treeview, filepath)