from dropbox import client, rest
from gi.repository import Gtk, Gdk

# add your app key and secret here
APP_KEY = ''
APP_SECRET = ''

class DropboxSession(object):
    TOKEN_FILE = "ingress_token_store.txt"

    def __init__(self, window):
        self.app_key = APP_KEY
        self.app_secret = APP_SECRET
        self.api_client = None
        self.code_entry = None
        self.login_button = None
        try:
            token = open(self.TOKEN_FILE).read()
            self.api_client = client.DropboxClient(token)
            print("loaded access token")
        except IOError:
            self.start_flow(window)

    def start_flow(self, window):
        self.flow = client.DropboxOAuth2FlowNoRedirect(self.app_key, self.app_secret)
        authorize_url = self.flow.start()

        self.code_entry = Gtk.Entry()
        self.code_entry.set_placeholder_text("Paste the authorization code here...")

        self.login_button = Gtk.Button.new_with_label("Login")
        self.login_button.connect("clicked", self.on_login_clicked)

        self.dialog = DropboxLoginDialog(window)
        self.dialog.build_dialog(authorize_url, self.code_entry, self.login_button)

    def finish_flow(self):
        try:
            access_token, user_id = self.flow.finish(self.code_entry.get_text().strip())
        except rest.ErrorResponse, e:
            print(e)
            return None

        with open(self.TOKEN_FILE, 'w') as f:
            f.write(access_token)
        self.api_client = client.DropboxClient(access_token)
        print(self.api_client.account_info())

    def on_login_clicked(self, button):
        self.finish_flow()
        self.dialog.destroy()

    def list_folders(self, path):
        try:
            return self.api_client.metadata(path)
        except rest.ErrorResponse, e:
            print(e)
            return None

    def rename_file(self, old_path, new_path):
        return self.move_file(old_path, new_path)

    def move_file(self, from_path, to_path):
        try:
            return self.api_client.file_move(from_path, to_path)
        except rest.ErrorResponse, e:
            print(e)
            return None

    def upload_file(self, dropbox_path, local_path):
        # TODO: Chunk Uploader
        try:
            with open(local_path, 'rb') as f:
                res = self.api_client.put_file(dropbox_path, f)
                return res
        except rest.ErrorResponse, e:
            print(e)
            return None

    def remove_file(self, filepath):
        try:
            return self.api_client.file_delete(filepath)
        except rest.ErrorResponse, e:
            print(e)
            return None


class DropboxLoginDialog(Gtk.Window):
    def __init__(self, window):
        Gtk.Window.__init__(self, title="Dropbox Access")
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self.set_transient_for(window)

    def build_dialog(self, url, code_entry, create_button):
        print("build_dialog")
        content_grid = Gtk.Grid()
        content_grid.set_margin_left(12)
        content_grid.set_margin_right(12)
        content_grid.set_margin_top(12)
        content_grid.set_margin_bottom(12)
        content_grid.set_row_spacing(6)
        content_grid.set_column_spacing(12)

        goto_link = Gtk.LinkButton(url, "1. Click Here")
        click_label = Gtk.Label("2. Click 'Allow'.")
        copy_label = Gtk.Label("3. Copy the authorization code.")

        # create button box
        buttonbox = Gtk.ButtonBox(Gtk.Orientation.HORIZONTAL)
        buttonbox.set_layout(Gtk.ButtonBoxStyle.END)
        cancel_button = Gtk.Button.new_from_stock(Gtk.STOCK_CANCEL)
        cancel_button.connect("clicked", self.on_cancel_clicked)

        buttonbox.pack_end(cancel_button, False, False, 0)
        buttonbox.pack_end(create_button, False, False, 0)

        content_grid.attach(goto_link, 0, 0, 1, 1)
        content_grid.attach(click_label, 0, 1, 1, 1)
        content_grid.attach(copy_label, 0, 2, 1, 1)
        content_grid.attach(code_entry, 0, 3, 1, 1)
        content_grid.attach(buttonbox, 0, 4, 1, 1)
        self.add(content_grid)
        self.show_all()

    def on_cancel_clicked(self, button):
        self.destroy()
