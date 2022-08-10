#!/usr/bin/env python3
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, Gst

import os
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3

import random

# from gi.repository import GSound
# from gi.repository.Pango import WrapMode


class WindowMain:

    def __init__(self):
        # Get GUI from Glade file
        self.builder = Gtk.Builder()
        self.builder.add_from_file("com/example/ui/win.glade")
        self.builder.connect_signals(self)

        self.song_playing = ""

        # Display main window
        self.windowMain = self.builder.get_object("windowMain")

        listbox = self.builder.get_object("lstSongs")
        self.listbox = listbox
        self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)

        Gst.init(None)
        self.player = Gst.ElementFactory.make("playbin", "player")
        fakesink = Gst.ElementFactory.make("fakesink", "fakesink")
        self.player.set_property("video-sink", fakesink)
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)

        self.loop = False
        self.randomplay = False
        self.songs_played = []
        self.lst_songs = []
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

    def _add_row(self, listbox, name, desc, clicked):
        row = Gtk.ListBoxRow()
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        label = Gtk.Label(label="<b>%s</b>\n%s" % (name, desc),
                          use_markup=True, wrap=True, wrap_mode=Pango.WrapMode.WORD_CHAR,
                          hexpand=True, xalign=0, yalign=0.5)
        box.add(label)

        row.add(box)
        listbox.insert(row, -1)

    def on_lstSongs_row_selected(self, listbox, listboxrow):
        filepath = self.songs[listboxrow.get_index()][0]
#        current_song = self.listbox.get_selected_row()
#        title = self.songs[listboxrow.get_index()][1]
#        album = self.songs[listboxrow.get_index()][3]
        playerState = self.player.get_state(0)

        if filepath not in self.song_playing:
            if playerState.state == Gst.State.PLAYING:
                self.player.set_state(Gst.State.NULL)
                self.song_playing = filepath

            self.player.set_property("uri", "file://" + filepath)
            self.player.set_state(Gst.State.PLAYING)

        else:
            if playerState.state == Gst.State.PLAYING:
                self.player.set_state(Gst.State.PAUSED)

            else:
                self.player.set_state(Gst.State.PLAYING)

    def playSong(self, path):
        print(path)

    def on_window_main_destroy(self, widget, data=None):
        Gtk.main_quit()

    def on_Quit_clicked(self, widget):
        Gtk.main_quit()

    def main(self):
        Gtk.main()

    def on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            current_song = self.listbox.get_selected_row()
            self.songs_played.append(current_song.get_index())
            self.player.set_state(Gst.State.NULL)
            self.play_next_song()
            # self.button.set_label("Start")
        elif t == Gst.MessageType.ERROR:
            self.player.set_state(Gst.State.NULL)
            err, debug = message.parse_error()
            print("Error: %s" % err, debug)
            self.button.set_label("Start")

    def on_loopbutton_toggled(self, _):
        self.loop = not self.loop

    def on_previousbutton_clicked(self, _):
        self.player.set_state(Gst.State.NULL)
        self.play_last_song()

    def on_skipbutton_clicked(self, _):
        self.player.set_state(Gst.State.NULL)
        current_song = self.listbox.get_selected_row()
        self.songs_played.append(current_song.get_index())
        self.play_next_song()

    def play_last_song(self):
        self.player.set_state(Gst.State.NULL)

        if len(self.songs_played) != 0:
            last_song = self.listbox.get_row_at_index(self.songs_played.pop(len(self.songs_played) - 1))
            self.listbox.select_row(last_song)
            self.on_lstSongs_row_selected(self.listbox, last_song)

    def play_next_song(self):
        if self.loop == False:
            if self.randomplay:
                next_song_num = random.randrange(0, len(self.listbox) - 1)
                next_song = self.listbox.get_row_at_index(next_song_num)

            else:
                current_song = self.listbox.get_selected_row()

                index = current_song.get_index() + 1
                if current_song.get_index() == len(self.listbox) - 1:
                    index = 0

                next_song = self.listbox.get_row_at_index(index)

            self.listbox.select_row(next_song)
            self.on_lstSongs_row_selected(self.listbox, next_song)
        else:
            self.player.set_state(Gst.State.PLAYING)

    def on_rndPlay_toggled(self, place_holder):
        self.randomplay = not self.randomplay

    def directory_entered(self, path):

        for root, subdirs, files in os.walk(path):
            list_file_path = os.path.join(root, 'my-directory-list.txt')

            with open(list_file_path, 'wb'):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file_path.endswith(".mp3"):
                        self.lst_songs.append([file_path])
                        metadata = MP3(file_path, ID3=EasyID3)
                        self.songs.append([file_path, metadata.get("title")[0], metadata.get("artist")[0], metadata.get("album")[0]])
                        self._add_row(self.listbox, metadata.get("title")[0], metadata.get("album")[0], None)

        self.windowMain.show_all()

if __name__ == "__main__":
    application = WindowMain()
    application.main()
