#!/usr/bin/env python3
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, Gst

import os
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3

# from gi.repository import GSound
# from gi.repository.Pango import WrapMode


class WindowMain:

    def __init__(self):
        # Get GUI from Glade file
        self.builder = Gtk.Builder()
        self.builder.add_from_file("com/example/ui/win.glade")
        self.builder.connect_signals(self)

        # Display main window
        self.windowMain = self.builder.get_object("windowMain")

        listbox = self.builder.get_object("lstSongs")
        self.listbox = listbox
        self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)

        self.songs = []

        self.windowMain.show_all()

    def onRootDirectorySelected(self, _):
        filechooserdialog = Gtk.FileChooserDialog("Open...", None, Gtk.FileChooserAction.SELECT_FOLDER, (
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        filechooserdialog.set_title("FileChooserDialog")
        response = filechooserdialog.run()

        if response == Gtk.ResponseType.OK:
            # print("File selected: %s" % filechooserdialog.get_filename())
            self.directory_entered(filechooserdialog.get_filename())

        filechooserdialog.destroy()


    def on_radio_button_toggled(self, radio, row):
        # If the radio button toggled to inactive, don't reactivate the row
        if not radio.get_active():
            return
        row.activate()

    def _add_row(self, listbox, name, desc, button, clicked):
        row = Gtk.ListBoxRow()
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        # button.set_valign(Gtk.Align.START)
        # button.connect("toggled", clicked, row)
        # box.add(button)

        label = Gtk.Label(label="<b>%s</b>\n%s" % (name, desc),
                          use_markup=True, wrap=True, wrap_mode=Pango.WrapMode.WORD_CHAR,
                          hexpand=True, xalign=0, yalign=0.5)
        box.add(label)

        row.add(box)
        listbox.insert(row, -1)

    def on_lstSongs_row_selected(self, listbox, listboxrow):
        songPath = self.songs[listboxrow.get_index()][1]
        print("Selected song %s" % (songPath))

    def playSong(self, path):
        print(path)

    def on_window_main_destroy(self, widget, data=None):
        Gtk.main_quit()

    def on_Quit_clicked(self, widget):
        Gtk.main_quit()

    def main(self):
        Gtk.main()

    def directory_entered(self, path):

        for root, subdirs, files in os.walk(path):
            list_file_path = os.path.join(root, 'my-directory-list.txt')

            with open(list_file_path, 'wb'):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file_path.endswith(".mp3"):
                        metadata = MP3(file_path, ID3=EasyID3)
                        filename = os.path.basename(file_path)
                        self.songs.append([file_path, metadata.get("title")[0], metadata.get("artist")[0]])
                        self._add_row(self.listbox, metadata.get("title")[0], metadata.get("artist")[0], None, None)

        self.windowMain.show_all()

if __name__ == "__main__":
    application = WindowMain()
    application.main()
