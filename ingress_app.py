#! /usr/bin/env python

from gi.repository import Gtk, Gdk, GObject
from ingress.main_window import IngressMainWindow

def main(argv):
    GObject.threads_init()
    Gdk.threads_init()
    win = IngressMainWindow()
    win.quit_main_window()
    Gtk.main()

if __name__ == '__main__':
    import sys
    main(sys.argv)