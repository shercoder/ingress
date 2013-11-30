from gi.repository import Gtk
from util import Util
from tagfs import TagLabel
import os, time

class FileGeneral(Gtk.Grid):
    def __init__(self, filepath, treeview):
        Gtk.Grid.__init__(self)
        self.set_row_spacing(2)
        self.set_column_spacing(10)
        self.set_margin_left(0)
        self.set_margin_right(0)
        self.set_margin_top(0)
        self.set_margin_bottom(0)
        self.set_name('FileGeneral')

        self._filepath = filepath
        self._treeview = treeview
        self._filestat = Util.get_file_stat(filepath)

        self.create_grid()

    def create_grid(self):
        general_header = Util.create_label("<big>GENERAL</big>",
                                        align=Gtk.Align.START)
        general_header.set_use_markup(True)

        self.attach(general_header, 0, 0, 1, 1)

        # create attribute labels
        filename_label = Util.create_label("Name:")
        filesize_label = Util.create_label("Filesize:")
        location_label = Util.create_label("Location:")
        last_modified_label = Util.create_label("Last Modified:")
        last_access_label = Util.create_label("Last Access:")

        # create attribute values
        filename = Util.create_info_label(os.path.basename(self._filepath))
        filesize = self.file_or_folder_size_widget()
        location = Util.create_info_label(os.path.dirname(self._filepath), ellipsize=True)
        last_modified = Util.create_info_label(time.ctime(self._filestat.st_mtime))
        last_access = Util.create_info_label(time.ctime(self._filestat.st_atime))

        # add all widgets to the grid
        self.attach(filename_label, 0, 1, 1, 1)
        self.attach(filename, 1, 1, 1, 1)
        self.attach(filesize_label, 0, 2, 1, 1)
        self.attach(filesize, 1, 2, 1, 1)
        self.attach(location_label, 0, 3, 1, 1)
        self.attach(location, 1, 3, 1, 1)
        self.attach(last_modified_label, 0, 4, 1, 1)
        self.attach(last_modified, 1, 4, 1, 1)
        self.attach(last_access_label, 0, 5, 1, 1)
        self.attach(last_access, 1, 5, 1, 1)

    def file_or_folder_size_widget(self):
        if os.path.isdir(self._filepath):
            btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            filesize = Gtk.Button(label="Calculate")
            filesize.connect("clicked", self.on_clicked_filesize_button)
            filesize.set_tooltip_text("Click to calculate")
            filesize.set_hexpand(False)
            btn_box.pack_start(filesize, False, False, 0)
            return btn_box
        else:
            size_of_file = str(Util.get_filesize_format(self._filestat.st_size))
            filesize = Util.create_info_label(size_of_file)
            filesize.set_size_request(50, 30)
            return filesize

    # callback for "Click to calculate" button
    def on_clicked_filesize_button(self, button):
        (model, treepaths) = self._treeview.get_selection().get_selected_rows()
        sel_iter = model.get_iter(treepaths[0])
        if os.path.isdir(model[sel_iter][1]):
            filesize = Util.get_dir_size(model[sel_iter][1])
            button.set_label(Util.get_filesize_format(filesize))

class FilePermissions(Gtk.Grid):
    def __init__(self, filepath, treeview):
        Gtk.Grid.__init__(self)
        self.set_row_spacing(2)
        self.set_column_spacing(10)
        self.set_margin_left(0)
        self.set_margin_right(0)
        self.set_margin_top(0)
        self.set_margin_bottom(0)
        self.set_name('FilePermissions')

        self._filepath = filepath
        self._treeview = treeview
        self._filestat = Util.get_file_stat(filepath)
        self._owner_name = Util.get_usrname_from_uid(self._filestat.st_uid).pw_name
        self._group_name = Util.get_grpname_from_gid(self._filestat.st_gid).gr_name

        self.build_grid()

    def build_grid(self):
        permissions_header = Util.create_label("<big>PERMISSIONS</big>",
                                        align=Gtk.Align.START)
        permissions_header.set_use_markup(True)
        self.attach(permissions_header, 0, 0, 1, 1)

        # create attribute labels
        owner_label = Util.create_label("Owner:")
        group_label = Util.create_label("Group:")
        perms_label = Util.create_info_label(
                            Util.create_perm_str(self._filestat.st_mode),
                            align=Gtk.Align.END)

        # create attribute values
        owner = Util.create_info_label(self._owner_name)
        group = Util.create_info_label(self._group_name)

        # Entry box
        perms_entry = Gtk.Entry.new()
        perms_entry.set_max_length(3)
        perms_entry.set_width_chars(3)
        perms_entry.set_text(Util.create_777_format(self._filestat.st_mode))
        perms_entry.connect("changed", self.on_perms_changed, perms_label)

        self.attach(owner_label, 0, 1, 1, 1)
        self.attach(group_label, 0, 2, 1, 1)
        self.attach(perms_label, 0, 3, 1, 1)
        self.attach(owner, 1, 1, 1, 1)
        self.attach(group, 1, 2, 1, 1)
        self.attach(perms_entry, 1, 3, 1, 1)

    def on_perms_changed(self, entry, perms_label):
        text = entry.get_text()
        if len(text) == 3 and Util.is_integer(text):
            (model, treepaths) = self._treeview.get_selection().get_selected_rows()
            treeiter = model.get_iter(treepaths[0])
            os.chmod(model[treeiter][1], int(text, 8))
            filestat = Util.get_file_stat(model[treeiter][1])
            perms_label.set_label(Util.create_perm_str(filestat.st_mode))

class FileTags(Gtk.Box):
    def __init__(self, filepath, index_manager):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(3)

        self._filepath = filepath
        self._index_manager = index_manager

        permissions_header = Util.create_label("<big>TAGS</big>",
                                        align=Gtk.Align.START)
        permissions_header.set_use_markup(True)
        self.pack_start(permissions_header, False, False, 0)

        add_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        tag_entry = Gtk.Entry()
        add_tag_button = Gtk.Button(label="Add Tag")
        add_tag_button.connect("clicked", self.on_clicked_add_tag, (filepath, tag_entry))
        add_box.pack_start(tag_entry, False, False, 0)
        add_box.pack_start(add_tag_button, False, False, 0)
        self.pack_start(add_box, False, False, 0)

        self._tags_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.pack_start(self._tags_container, False, False, 0)
        self.show_all_tags()

    def show_all_tags(self):
        for child in self._tags_container.get_children():
            child.destroy()

        tags = self._index_manager.get_tags_for_filepath(self._filepath)
        if tags:
            tags_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
            tags = tags = str(tags).split(' ')
            row = 14
            for i, tag in enumerate(tags):
                if i%5 == 0:
                    self._tags_container.pack_start(tags_box, False, False, 0)
                    tags_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
                    row += 1
                tag_label = TagLabel(tag)
                tag_label.connect("close-clicked",
                            self.on_tag_label_close_clicked,
                            self._filepath, tags_box)
                tags_box.pack_start(tag_label, False, False, 0)
            self._tags_container.pack_start(tags_box, False, False, 0)
            self._tags_container.show_all()
            self.show_all()

    def on_clicked_add_tag(self, button, user_data):
        filepath, entry = user_data
        tags = entry.get_text()

        #make tags' list
        tags = tags.split()

        # get old tags
        old_tags = self._index_manager.get_tags_for_filepath(self._filepath)
        old_tags = old_tags.split()

        # get unique tags from new and old tags
        unique_tags = set(tags + old_tags)
        unique_tags = ' '.join(list(unique_tags))

        self._index_manager.update_document(filepath, unique_tags)
        self.show_all_tags()

    def on_tag_label_close_clicked(self, tag_label, filepath, box):
        self._index_manager.delete_tag(filepath, tag_label.label.get_text())
        tag_label.destroy()