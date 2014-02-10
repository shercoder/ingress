from gi.repository import Gtk, Gdk
import os

# logger
import logging
logger = logging.getLogger(__name__)

(DROPBOX_FILEPATH, LOCAL_FILEPATH) = range(2)

class DropboxPaned(Gtk.Paned):
    def __init__(self):
        Gtk.Paned.__init__(self)

class DropboxTreeStore(Gtk.TreeStore):
    def __init__(self, session, source_path="/"):
        Gtk.TreeStore.__init__(self, str, str, bool)
        self.session = session
        self.generate_tree(source_path)

    def generate_tree(self, path, parent=None):
        if parent is None:
            self.clear()
            parent = self.append(parent, ["Dropbox", path, True])
            self.append(parent, None)
        else:
            self.remove(self.iter_children(parent))
            folder_metadata = self.session.list_folders(path)
            if folder_metadata:
                for file_metadata in folder_metadata['contents']:
                    filepath = file_metadata['path']
                    if file_metadata['is_dir']:
                        child_parent = self.append(parent, [os.path.basename(filepath), filepath, True])
                        self.append(child_parent, None)
                    else:
                        self.append(parent, [os.path.basename(filepath), filepath, False])

class DropboxTreeView(Gtk.TreeView):
    TARGETS = [
        ('INGRESS_TREE_MODEL_ROW', Gtk.TargetFlags.SAME_WIDGET|Gtk.TargetFlags.OTHER_WIDGET, 0)
    ]

    def __init__(self, treestore, parent_window):
        Gtk.TreeView.__init__(self, treestore)
        self.parent_window = parent_window
        self.set_enable_tree_lines(True)

        self.set_name('DropboxTreeView')
        self.set_headers_visible(False)

        renderer = Gtk.CellRendererText()
        renderer.set_property("editable", True)
        renderer.connect("edited", self.on_filename_edited)
        column = Gtk.TreeViewColumn(None, renderer, text=0)
        self.append_column(column)
        self.connect("test-expand-row", self.on_row_expanded)
        self.connect("row-collapsed", self.on_row_collapsed)

        # drag and drop setting
        self.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK,
                                        self.TARGETS,
                                        Gdk.DragAction.DEFAULT | Gdk.DragAction.MOVE)
        self.enable_model_drag_dest(self.TARGETS, Gdk.DragAction.DEFAULT)

        self.drag_dest_add_text_targets()
        self.drag_source_add_text_targets()

        self.connect("drag-data-get", self._dnd_get_data_dropbox)
        self.connect("drag-data-received", self._dnd_data_received_dropbox)

        # self.get_selection().connect("changed", self.on_tree_selection_changed)

        # create pop up menu on right click
        self.connect("button_press_event",self.on_right_click)

        # set multiple selection
        # self.get_selection().set_mode(Gtk.SelectionMode.MULTIPLE)

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

    def _dnd_data_received_dropbox(self, treeview, context, x, y, selection, targetType, time):
        model = treeview.get_model()
        data = selection.get_data()
        drop_info = treeview.get_dest_row_at_pos(x, y)
        if drop_info:
            path, position = drop_info
            iterator = model.get_iter(path)

            #if on drop is a file
            if not model[iterator][2]:
                iterator = model.iter_parent(iterator)
            dest_path = os.path.join(model[iterator][1], os.path.basename(data))
            res = self.get_model().session.upload_file(dest_path, data)
            if res:
                model.append(iterator, [os.path.basename(res['path']), res['path'], res['is_dir']])

            # update treeview
            treepath = model.get_path(iterator)
            self.collapse_row(treepath)
            self.expand_to_path(treepath)

        if Gdk.DragAction.MOVE == context.get_actions():
            context.finish(True, True, time)
        return

    def _dnd_get_data_dropbox(self, treeview, context, selection, targetType, eventTime):
        treeselection = treeview.get_selection()
        model, treepaths = treeselection.get_selected_rows()

        # get the first iter, don't allow multiple selection drag n drop
        iterator = model.get_iter(treepaths[0])
        data = model.get_value(iterator, 1)
        selection.set(selection.get_target(), 8, data)
        self.parent_window.drop_from_dropbox = True

    def on_filename_edited(self, widget, path, text):
        old_path = self.get_model()[path][1]

        # cannot change user's home dir name
        if old_path is not '/':
            parent_path = os.path.dirname(old_path)
            new_path = os.path.join(parent_path, text)
            if self.get_model().session.rename_file(old_path, new_path):
                self.get_model()[path][0] = text
                self.get_model()[path][1] = new_path

    def add_popup_menu(self, filepath, parent_iter):
        self.popup = Gtk.Menu()

        # remove file from dropbox
        remove_label = Gtk.MenuItem(label="Remove from Dropbox")
        remove_label.connect("activate", self.on_activate_remove_file, filepath, parent_iter)
        self.popup.append(remove_label)

        # download file
        # download_label = Gtk.MenuItem(label="Download from Dropbox")
        # download_label.connect("activate", self.on_activate_download_file, filepath, parent_iter)
        # self.popup.append(download_label)
        # self.popup.show_all()

    def on_right_click(self, treeview, event):
        if event.button == 3: # right click
            pthinfo = treeview.get_path_at_pos(event.x, event.y)
            if pthinfo is not None:
                path, col, cellx, celly = pthinfo
                treeview.grab_focus()
                # treeview.set_cursor(path, col, 0)
                iter = self.get_model().get_iter(path)
                parent_iter = self.get_model().iter_parent(iter)
                self.add_popup_menu(self.get_model()[iter][1], parent_iter)
                self.popup.popup(None, None, None, None, event.button, event.time)
            return True

    def on_activate_remove_file(self, widget, filepath, parent_iter):
        if self.get_model().session.remove_file(filepath):
            treepath = self.get_model().get_path(parent_iter)
            self.collapse_row(treepath)
            self.expand_to_path(treepath)