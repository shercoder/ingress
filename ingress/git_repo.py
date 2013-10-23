from pygit2 import Repository as _Repository
from pygit2 import *
from gi.repository import Gtk

class Repository(_Repository):
    def __init__(self, repopath):
        super().__init__(repopath)

    def get_cur_branch(self):
        for b in self.branches():
            branch = self.lookup_branch(b)
            if branch.is_head(): branch.branch_name

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
