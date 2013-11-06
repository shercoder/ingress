#!/usr/bin/python3

from gi.repository import Gtk, Gdk
from send2trash import send2trash
from constants import *
import os

class IngressTreeStore(Gtk.TreeStore):
    def __init__(self):
        super(IngressTreeStore, self).__init__(str, str)
        self.generate_tree(HOME)


    def generate_tree(self, path, parent=None):
        if parent is None:
            self.clear()
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

    def generate_search_tree(self, files):
        if files:
            self.clear()
            for filename, filepath in files:
                self.append(None, [filename, filepath])

    # Override draggable and droppable methods from Gtk.TreeDragSource and Gtk.TreeDragDest
    def row_draggable(self, path):
        print(path)
        iter = self.get_iter(path)
        print(iter)

    def row_drop_possible(self, dest_path, selection_data):
        print(dest_path)

class IngressTreeView(Gtk.TreeView):
    def __init__(self, treestore):
        super(IngressTreeView, self).__init__(treestore)
        self.set_name('IngressTreeView')
        self.set_headers_visible(False)


        self.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK, [('text/plain', 0, 0)], Gdk.DragAction.MOVE)
        self.enable_model_drag_dest([('text/plain', 0, 0)], Gdk.DragAction.DEFAULT)

        self.connect("drag_data_get", self._dnd_get_data)
        self.connect("drag_data_received", self._dnd_data_received)
        # self.connect("drag_end", )

        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(None, renderer, text=0)
        self.append_column(column)
        self.connect("test-expand-row", self.on_row_expanded)
        self.connect("row-collapsed", self.on_row_collapsed)

        # create pop up menu on right click
        self.add_popup_menu()
        self.connect("button_press_event",self.on_right_click)

    def add_popup_menu(self):
        self.popup = Gtk.Menu()
        # self.popup.append(Gtk.MenuItem(label="Cut"))
        # self.popup.append(Gtk.MenuItem(label="Copy"))
        # self.popup.append(Gtk.MenuItem(label="Paste"))
        # self.popup.append(Gtk.MenuItem(label="Rename"))

        # send file to trash
        move2trash = Gtk.MenuItem(label="Move To Trash")
        move2trash.connect("activate", self.on_activate_move_2_trash)
        self.popup.append(move2trash)

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
                # model, path = treeview.get_path_at_pos(int(event.x), int(event.y))
                pthinfo = treeview.get_path_at_pos(event.x, event.y)
                if pthinfo is not None:
                    path, col, cellx, celly = pthinfo
                    treeview.grab_focus()
                    treeview.set_cursor(path, col, 0)
                    self.popup.popup(None, None, None, None, event.button, event.time)
                return True

    def on_activate_move_2_trash(self, widget):
        selection = self.get_selection()
        model, iter = selection.get_selected()
        filepath = model[iter][1]
        parent = model.iter_parent(iter)
        if parent is not None:
            parent_path = model.get_path(parent)
            send2trash(filepath)
            self.collapse_row(parent_path)
            self.expand_to_path(parent_path)

    # drag and drop callbacks
    def _dnd_get_data(self, view, context, selection, targetType, eventTime):
        treeselection = view.get_selection()
        model, iter = treeselection.get_selected()
        data = model.get_value(iter, 0)
        selection.set(selection.target, 8, data)

    def _dnd_data_received(self, widget, context, x, y, selection, targetType, time):
        model = treeview.get_model()
        data = selection.data
        drop_info = treeview.get_dest_row_at_pos(x, y)
        if drop_info:
            path, position = drop_info
            iter = model.get_iter(path)
            if (position == gtk.TREE_VIEW_DROP_BEFORE or position == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE):
                model.insert_before(iter, [data])
            else:
                model.insert_after(iter, [data])
        else:
            model.append([data])
            if context.action == gtk.gdk.ACTION_MOVE:
                context.finish(True, True, etime)

