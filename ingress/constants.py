#!/usr/bin/python3

from os.path import expanduser, join

HOME = expanduser("~")
INDEX_DIR = join(HOME, ".ingress_index/")

# dimensions
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 500
LEFT_PANED_WIDTH = 300

# permissions
rwx = ["---", "--x", "-w-", "-wx", "r--", "r-x", "rw-", "rwx"]
rwx_num = [0, 1, 2, 3, 4, 5, 6, 7]