#!/usr/bin/env python3
import gi
import sys
import threading
import time

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

        self.progressBar = self.builder.get_object("progressBar")

        listbox = self.builder.get_object("lstSongs")
        self.listbox = listbox
        self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)

        Gst.init(None)
        self.player = Gst.ElementFactory.make("playbin", "player")
        fakesink = Gst.ElementFactory.make("fakesink", "fakesink")
        self.player.set_property("video-sink", fakesink)

        # are we playing?
        self.playing = False
        # should we terminate execution?
        self.terminate = False
        # is seeking enabled for this media?
        self.seek_enabled = False
        # have we performed the seek already?
        self.seek_done = False
        # media duration (ns)
        self.duration = Gst.CLOCK_TIME_NONE

        self.progress_handler = None
        self.exiting = False

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
            self.play_song()

        else:
            if playerState.state == Gst.State.PLAYING:
                self.player.set_state(Gst.State.PAUSED)

            else:
                self.play_song()

    def playSong(self, path):
        print(path)

    def on_window_main_destroy(self, widget, data=None):
        self.player.set_state(Gst.State.NULL)
        self.progress_handler.cancel()
        self.exiting = True
        Gtk.main_quit()

    def on_Quit_clicked(self, widget):
        self.player.set_state(Gst.State.NULL)
        self.progress_handler.cancel()
        self.exiting = True
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

        elif t == Gst.MessageType.ERROR:
            self.player.set_state(Gst.State.NULL)
            err, debug = message.parse_error()
            print("Error: %s" % err, debug)
            self.button.set_label("Start")

        elif t == Gst.MessageType.DURATION_CHANGED:
            self.duration = Gst.CLOCK_TIME_NONE

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
        if self.progress_handler:
            self.progress_handler.cancel()

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
            self.play_song()

    def play_song(self):
        ret = self.player.set_state(Gst.State.PLAYING)

        if ret == Gst.StateChangeReturn.FAILURE:
            print("ERROR: Unable to set the pipeline to the playing state")
            sys.exit(1)

        self.progress_handler = threading.Timer(1.0, self.handle_song_progress)
        self.progress_handler.start()

    def handle_song_progress(self):
        try:
            # listen to the bus
            bus = self.player.get_bus()
            while True and not self.exiting:
                time.sleep(0.5)
                msg = bus.timed_pop_filtered(
                    100 * Gst.MSECOND,
                    (Gst.MessageType.STATE_CHANGED | Gst.MessageType.ERROR
                        | Gst.MessageType.EOS | Gst.MessageType.DURATION_CHANGED)
                )

                # parse message
                if msg:
                    self.on_message(bus, msg)
                else:
                    # we got no message. this means the timeout expired
                    if self.player:
                        current = -1
                        # query the current position of the stream
                        ret, current = self.player.query_position(
                            Gst.Format.TIME)
                        if not ret:
                            print("ERROR: Could not query current position")

                        # if we don't know it yet, query the stream duration
                        if self.duration == Gst.CLOCK_TIME_NONE:
                            (ret, self.duration) = self.player.query_duration(
                                Gst.Format.TIME)
                            if not ret:
                                print("ERROR: Could not query stream duration")

                        # print current position and total duration
                        # print("Position {0} / {1}".format(current, self.duration))

                        prog = current / self.duration
                        print(prog)
                        self.progressBar.set_fraction(prog)

                        # if seeking is enabled, we have not done it yet and the time is right,
                        # seek
                        if self.seek_enabled and not self.seek_done and current > 10 * Gst.SECOND:
                            print("Reached 10s, performing seek...")
                            self.player.seek_simple(
                                Gst.Format.TIME, Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, 30 * Gst.SECOND)

                            self.seek_done = True
                if self.terminate:
                    break
        finally:
            self.player.set_state(Gst.State.NULL)

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
