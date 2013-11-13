#!/usr/bin/python3

from gi.repository import Gtk
import os, pwd, grp, stat
from pygit2 import Repository as _Repository
from constants import *

class Util(object):
    @staticmethod
    def create_label(label_name, align=Gtk.Align.END):
        markup = "<b>%s</b>" % label_name
        label = Gtk.Label(label=markup)
        label.set_use_markup(True)
        label.set_halign(align)
        # label.set_justify(Gtk.Justification.RIGHT)
        return label

    @staticmethod
    def create_info_label(label_name,  align=Gtk.Align.START):
        label = Gtk.Label(label=label_name)
        label.set_halign(align)
        return label

    @staticmethod
    def get_file_stat(filepath):
        return os.lstat(filepath)

    @staticmethod
    def get_filesize_format(filesize):
        for size_type in ['bytes', 'KB', 'MB', 'GB', 'TB']:
            if filesize < 1024.0:
                return "%3.1f %s" % (filesize, size_type)
            filesize /= 1024.0

    @staticmethod
    def get_dir_size(dirpath):
        total_size = 0
        for path, dirnames, filenames in os.walk(dirpath):
            for f in filenames:
                fp = os.path.join(path, f)
                try:
                    total_size += os.path.getsize(fp)
                except OSError:
                    pass
        return total_size

    @staticmethod
    def get_usrname_from_uid(uid):
        return pwd.getpwuid(uid)

    @staticmethod
    def get_grpname_from_gid(gid):
        return grp.getgrgid(gid)

    @staticmethod
    def create_perm_str(mode):
        if stat.S_ISREG(mode):
            perms = '-'
        elif stat.S_ISDIR(mode):
            perms = 'd'
        elif stat.S_ISLNK(mode):
            perms = 'l'
        perms += "%s%s%s" % (
            rwx[((mode & stat.S_IRWXU) >> 6)],
            rwx[((mode & stat.S_IRWXG) >> 3)],
            rwx[(mode & stat.S_IRWXO)]
        )
        return perms

    @staticmethod
    def create_777_format(mode):
        return "%s%s%s" % (
            ((mode & stat.S_IRWXU) >> 6),
            ((mode & stat.S_IRWXG) >> 3),
            (mode & stat.S_IRWXO)
        )

    @staticmethod
    def is_integer(entry):
        try:
            int(entry)
            return True
        except ValueError:
            return False

    # Git related methods
    @staticmethod
    def has_git_repo(filepath):
        try:
            _Repository(filepath)
            return True
        except KeyError:
            return False

    # Other
    @staticmethod
    def clear_notebook(notebook):
        for page in notebook.get_children():
                notebook.remove(page)


# class KeyValueBox(Gtk.Alignment):
#     def __init__(self, key, value):
#         super(KeyValueBox, self).__init__()
#         self.set(1, 0, 0, 0)
#         self.set_homogeneous(True)
#         self.pack_start(key, True, True, 10)
#         self.pack_start(value, True, True, 0)

class KeyValueBox(Gtk.Box):
    def __init__(self, key, value):
        super(KeyValueBox, self).__init__((Gtk.Orientation.HORIZONTAL, 5))
        self.set_homogeneous(True)
        self.pack_start(key, True, True, 10)
        self.pack_start(value, True, True, 0)
