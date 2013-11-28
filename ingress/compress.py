from gi.repository import Gtk, Gdk
from util import Util
import os

compress_types = {".ar": "ar r", ".tar": "tar -cf", ".tar.gz": "tar -czf", ".zip": "zip -r"}

class CompressDialog(Gtk.Window):
    def __init__(self, window, treeview, filepath):
        Gtk.Window.__init__(self, title="Compress")
        self._filepath = filepath
        self._treeview = treeview
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self.set_transient_for(window)
        # self.set_size_request(400, 150)
        self.build_dialog()
        self.show_all()

    def build_dialog(self):
        content_grid = Gtk.Grid()
        content_grid.set_margin_left(12);
        content_grid.set_margin_right(12);
        content_grid.set_margin_top(12);
        content_grid.set_margin_bottom(12);
        content_grid.set_row_spacing(6)
        content_grid.set_column_spacing(12);

        # subgrid
        subgrid = Gtk.Grid()
        subgrid.set_margin_left(0);
        subgrid.set_margin_right(0);
        subgrid.set_margin_top(0);
        subgrid.set_margin_bottom(0);
        subgrid.set_row_spacing(6)
        subgrid.set_column_spacing(12);

        # subgrid upper row
        filename_label = Util.create_simple_label("Filename:")
        self._filename_entry = Gtk.Entry()

        # subgrid filetype combobox
        self._compress_list_store = self.create_compress_list_store()
        self._compress_type_combo = Gtk.ComboBox.new_with_model(self._compress_list_store)
        self._compress_type_combo.set_active(0)
        renderer_text = Gtk.CellRendererText()
        self._compress_type_combo.pack_start(renderer_text, True)
        self._compress_type_combo.add_attribute(renderer_text, "text", 0)

        subgrid.attach(filename_label, 0, 0, 1, 1)
        subgrid.attach(self._filename_entry, 1, 0, 1, 1)
        subgrid.attach(self._compress_type_combo, 2, 0, 1, 1)

        # subgrid bottom row
        location_label = Util.create_simple_label("Location:")
        self.create_filechooser_dialog()
        self._select_location_button = Gtk.FileChooserButton.new_with_dialog(self._dialog)
        self._select_location_button.set_current_folder(os.path.dirname(self._filepath))
        subgrid.attach(location_label, 0, 1, 1, 1)
        subgrid.attach(self._select_location_button, 1, 1, 2, 1)


        # create button box
        buttonbox = Gtk.ButtonBox(Gtk.Orientation.HORIZONTAL)
        buttonbox.set_layout(Gtk.ButtonBoxStyle.END)
        cancel_button = Gtk.Button.new_from_stock(Gtk.STOCK_CANCEL)
        create_button = Gtk.Button.new_with_label("Create")
        cancel_button.connect("clicked", self.on_cancel_clicked)
        create_button.connect("clicked", self.on_create_clicked)
        buttonbox.pack_end(cancel_button, False, False, 0)
        buttonbox.pack_end(create_button, False, False, 0)

        content_grid.attach(subgrid, 0, 0, 1, 1)
        content_grid.attach(buttonbox, 0, 1, 1, 1)

        self.add(content_grid)
        self.show_all()

    def create_compress_list_store(self):
        store = Gtk.ListStore(str, str)
        for k,v in compress_types.items():
            store.append([k, v])
        return store

    def create_filechooser_dialog(self):
        self._dialog = Gtk.FileChooserDialog("Please choose a folder", self,
            Gtk.FileChooserAction.SELECT_FOLDER,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            "Select", Gtk.ResponseType.OK))
        self._dialog.set_default_size(800, 400)

    def on_cancel_clicked(self, button):
        self.destroy()

    def on_create_clicked(self, button):
        current_folder = self._select_location_button.get_current_folder()
        iter = self._compress_type_combo.get_active_iter()
        compress_type = self._compress_list_store[iter][1]

        archive_filename = self._filename_entry.get_text().strip()
        if archive_filename:
            # get all selected files/folders paths
            allpaths = []
            model, treepaths = self._treeview.get_selection().get_selected_rows()
            for treepath in treepaths:
                allpaths.append(model[model.get_iter(treepath)][1])

            if allpaths:
                allpaths = ' '.join(allpaths)
                archive_filename = os.path.join(current_folder, archive_filename)
                command = compress_type + ' ' + archive_filename + ' ' + allpaths
                import subprocess
                output, error = subprocess.Popen(
                                    command.split(' '), stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE).communicate()
                # self._treeview.collapse_row(parent_path)
                # self._treeview.expand_to_path(parent_path)
                self.destroy()