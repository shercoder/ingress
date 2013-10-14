#!/usr/bin/python3

from gi.repository import Gtk
import os

class Util(object):
    @staticmethod
    def create_label(label_name):
        return Gtk.Label(label=label_name)

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