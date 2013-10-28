#!/usr/bin/python

from whoosh.fields import SchemaClass, TEXT, KEYWORD, ID, STORED
from whoosh import index, writing
from whoosh.qparser import QueryParser
from gi.repository import Gtk, GObject
from constants import INDEX_DIR
import os

class FilenameSchema(SchemaClass):
    filepath = ID(stored=True, unique=True)
    filename = TEXT(stored=True)
    tags = KEYWORD(stored=True, lowercase=True, scorable=True)

class IndexManager(object):
    def create_index(self):
        self.create_index_dir()
        return index.create_in(INDEX_DIR, FilenameSchema)

    def open_index(self):
        if index.exists_in(INDEX_DIR):
            return index.open_dir(INDEX_DIR)
        else:
            return self.create_index()

    def create_index_dir(self):
        if not os.path.exists(INDEX_DIR):
            os.mkdir(INDEX_DIR)

    def clear_index(self):
        with self.open_index().writer() as writer:
            writer.mergetype = writing.CLEAR

    def add_new_document(self, path, alltags):
        writer = self.open_index().writer()
        basename = os.path.basename(path)
        writer.add_document(filepath=unicode(path), filename=unicode(basename), tags=unicode(alltags))
        writer.commit()

    def update_document(self, path, alltags):
        writer = self.open_index().writer()
        basename = os.path.basename(path)
        writer.update_document(filepath=unicode(path), filename=unicode(basename), tags=unicode(alltags))
        writer.commit()

    def search_documents(self, query, field="tags"):
        index = self.open_index()
        qp = QueryParser(field, schema=index.schema)
        q = qp.parse(unicode(query))
        with index.searcher() as searcher:
            results = searcher.search(q, limit=None)
            new_results = [hit.fields() for hit in results]
        return new_results

    def get_tags_for_filepath(self, filepath):
        index = self.open_index()
        with index.searcher() as searcher:
            result = searcher.document(filepath=filepath)
        if result:
            return result['tags']
        return None

    def delete_tag(self, filepath, tag):
        tags = self.get_tags_for_filepath(filepath)
        if tags:
            tags = str(tags).replace(tag, '').strip()
            self.update_document(filepath, tags)


class TagLabel(Gtk.Box):
    __gsignals__ = {
        "close-clicked": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
    }
    def __init__(self, label_text):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.set_spacing(1)

        # label
        self.label = Gtk.Label(label_text)
        self.pack_start(self.label, False, True, True)

        # close button
        button = Gtk.Button()
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.set_focus_on_click(False)
        button.add(Gtk.Image.new_from_stock(Gtk.STOCK_CLOSE, Gtk.IconSize.MENU))
        button.connect("clicked", self.button_clicked)
        data =  ".button {\n" \
                "-GtkButton-default-border : 0px;\n" \
                "-GtkButton-default-outside-border : 0px;\n" \
                "-GtkButton-inner-border: 0px;\n" \
                "-GtkWidget-focus-line-width : 0px;\n" \
                "-GtkWidget-focus-padding : 0px;\n" \
                "padding: 0px;\n" \
                "}"
        provider = Gtk.CssProvider()
        provider.load_from_data(data)
        # 600 = GTK_STYLE_PROVIDER_PRIORITY_APPLICATION
        button.get_style_context().add_provider(provider, 600)
        self.pack_start(button, False, False, 0)

        self.show_all()

    def button_clicked(self, button, data=None):
            self.emit("close-clicked")
