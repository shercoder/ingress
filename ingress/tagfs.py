#!/usr/bin/python

from whoosh.fields import SchemaClass, TEXT, KEYWORD, ID, STORED
from whoosh.index import create_in
from gi.repository import Gtk

class FilenameSchema(SchemaClass):
    filepath = ID(stored=True, unique=True)
    filename = TEXT(stored=True)
    tags = KEYWORD(stored=True, lowercase=True, scorable=True)


# create schema
# schema = create_in("/dir/path/to/store/index", FilenameSchema)

class TagLabel(Gtk.Box):
    """docstring for TagLabel"""
    def __init__(self, label_text):
        Gtk.Box.__init__(self)
        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.set_spacing(1)

        # label
        label = Gtk.Label(label_text)
        self.pack_start(label, False, True, True)

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
            self.emit("clicked")
