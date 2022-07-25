#!/usr/bin/env python3
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, Gst
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
        listbox.set_selection_mode(Gtk.SelectionMode.NONE)

        buttonLabel = Gtk.ToggleButton()
        self._add_row(listbox, "asdfasdf", "asdfasdf asdfasdfasd asdfasd", buttonLabel, self.on_radio_button_toggled)

        self.windowMain.show_all()

    def on_radio_button_toggled(self, radio, row):
        # If the radio button toggled to inactive, don't reactivate the row
        if not radio.get_active():
            return
        row.activate()

    def _add_row(self, listbox, name, desc, button, clicked):
        row = Gtk.ListBoxRow()
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        button.set_valign(Gtk.Align.START)
        button.connect("toggled", clicked, row)
        box.add(button)

        label = Gtk.Label(label="<b>%s</b>\n%s" % (name, desc),
                          use_markup=True, wrap=True, wrap_mode=Pango.WrapMode.WORD_CHAR,
                          hexpand=True, xalign=0, yalign=0.5)
        box.add(label)

        row.add(box)
        listbox.prepend(row)

    def playSong(self, path):
        print(path)

    def on_window_main_destroy(self, widget, data=None):
        Gtk.main_quit()

    def on_Quit_clicked(self, widget):
        Gtk.main_quit()

    def main(self):
        Gtk.main()


if __name__ == "__main__":
    application = WindowMain()
    application.main()
