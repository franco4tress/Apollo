import bs4
from PIL import Image
import urllib3

import requests
from gi.overrides.GLib import GLib
from gi.overrides.GdkPixbuf import Pixbuf, GdkPixbuf


def getWikiData(artist, song_name):
    curatedname = song_name.replace(" ", "-")
    http = urllib3.PoolManager()

    response = http.request("GET", "https://genius.com/{}-{}-lyrics".format(artist, curatedname))
    if response is not None:
        html = bs4.BeautifulSoup(response.data, 'html.parser')

        # title = html.select("#firstHeading")[0].text
        infobox = html.find_all("img", class_="SizedImage__NoScript-sc-1hyeaua-2 UJCmI")

        url = infobox[0]["src"]
        response = requests.get(url)
        content = response.content

        loader = GdkPixbuf.PixbufLoader()

        print([loader.get_extensions() for loader in GdkPixbuf.Pixbuf.get_formats()])

        loader.write_bytes(GLib.Bytes.new(content))
        loader.close()

        # SizedImage__Image-sc-1hyeaua-1 iMdmgx

        return loader.get_pixbuf()
