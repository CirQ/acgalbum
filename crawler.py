import re
import urllib2
import sqlite3 as sqlite
import pickle
import imagehash
from io import BytesIO
from bs4 import BeautifulSoup
from bs4.element import Tag
from PIL import Image

class animelo_crawler(object):
    HOST = "https://pc.animelo.jp"
    DBPATH = "db/development.sqlite3"
    SAVEPATH = "app/assets/images/"
    RE_artist = re.compile(r"^/portals/artist/\d+$")
    RE_album = re.compile(r"^/portals/album/\d+$")
    RE_song = re.compile(r"^/portals/product/\d+$")
    RE_imgkey = re.compile(r"^.*&key=([0-9a-f]+)$")

    def __init__(self):
        self.CONNECT = sqlite.connect(self.DBPATH)
        self.CURSOR = self.CONNECT.cursor()

    def __del__(self):
        self.CURSOR.close()
        self.CONNECT.commit()
        self.CONNECT.close()

    def src_items_album(self, uri):
        text = urllib2.urlopen(self.HOST + uri).read()
        tree = BeautifulSoup(text, "lxml")
        root = tree.find("ul", class_="product-list")
        for child in root.children:
            if type(child) == Tag:
                yield child

    def parse_album(self, item):
        img_src = item.find("img", class_="main-image")["src"]
        img_bytes = BytesIO(urllib2.urlopen(img_src).read())
        album_cover = Image.open(img_bytes)

        detail = item.find("div", class_="detail")
        artist = detail.find("a", href=self.RE_artist)
        album = detail.find("a", href=self.RE_album)
        description = detail.find("p", class_="description")

        album_name = album.string
        album_site = album["href"]
        album_description = description.string.strip() if description.string else ""
        album_coverpath = self.RE_imgkey.match(img_src).group(1)
        album_fingerprint = str(imagehash.phash(album_cover))
        artist_name = artist.string
        artist_site = artist["href"]

        return album_cover, [album_name, album_site, album_description, album_coverpath, album_fingerprint], (artist_name, artist_site)

    def save_album(self, cover, album, artist):
        cover.save("%s%s.jpg" % (self.SAVEPATH, album[3]))
        artist_id = self.CURSOR.execute("select id from artists where name=?;", (artist[0],)).fetchone()
        if not artist_id:
            self.CURSOR.execute("insert into artists(name,site) values(?,?);", artist)
            artist_id = self.CURSOR.execute("select id from artists where name=?;", (artist[0],)).fetchone()
        album.append(artist_id[0])
        self.CURSOR.execute("insert into albums(name,site,description,coverpath,fingerprint,artist_id) values(?,?,?,?,?,?);", album)
        self.save_song(album)
    
    def src_items_song(self, uri):
        text = urllib2.urlopen(self.HOST + uri).read()
        tree = BeautifulSoup(text, "lxml")
        root = tree.find("ul", class_="product-list")
        for child in root.find_all("li"):
            yield child.find(class_="detail")

    def parse_song(self, item):
        song = item.find("a", href=self.RE_song)
        artist = item.find("a", href=self.RE_artist)
        description = item.find("p", class_="description")
        
        song_name = song.string
        song_site = song["href"]
        song_description = description.string.strip() if description.string else ""
        artist_name = artist.string
        artist_site = artist["href"]

        return [song_name, song_site, song_description], (artist_name, artist_site)

    def save_song(self, album):
        for item in self.src_items_song(album[1]):
            song, artist = self.parse_song(item)
            artist_id = self.CURSOR.execute("select id from artists where name=?;", (artist[0],)).fetchone()
            if not artist_id:
                self.CURSOR.execute("insert into artists(name,site) values(?,?);", artist)
                artist_id = self.CURSOR.execute("select id from artists where name=?;", (artist[0],)).fetchone()
            album_id = self.CURSOR.execute("select id from albums where name=?;", (album[0],)).fetchone()
            song.extend([artist_id[0], album_id[0]])
            self.CURSOR.execute("insert into songs(name,site,description,artist_id,album_id) values(?,?,?,?,?);", song)

        
    def main(self, uri):
        for item in self.src_items_album(uri):
            cover, album, artist = self.parse_album(item)
            album_id = self.CURSOR.execute("select id from albums where name=?;", (album[0],)).fetchone()
            if not album_id:
                print "saving", album[0]
                self.save_album(cover, album, artist)
            else:
                print "album already exists", album[0]
    
    def dump_fingerprint(self):
        self.CURSOR.execute("select id, fingerprint from albums;")
        rows = self.CURSOR.fetchall()
        rows = filter(lambda t:type(t[1])==unicode, rows)
        with open("fp.pkl", "w") as w:
            pickle.dump(rows, w)


if __name__ == '__main__':
    ac = animelo_crawler()
    ac.main("/ranking/monthly/album/")
    ac.main("/ranking/weekly/album/")
    ac.dump_fingerprint()
