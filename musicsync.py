"""
    musicsync.py

    Forked from Tom Graham's program, but uses tuple inputs of artists/titles rather than reading and uploading mp3s.


    API used: https://github.com/simon-weber/Unofficial-Google-Music-API
    Thanks to: Tom Graham, Kevion Kwok and Simon Weber

    Use at your own risk - especially for existing playlists

    Free to use, reuse, copy, clone, etc

    Usage:
     ms = MusicSync()
     # Will prompt for Email and Password - if 2-factor auth is on you'll need to generate a one-
       time password
     ms.sync_playlist( [("artist","song")] )
"""
__author__ = "Mac Gaulin"
__email__ = "git@mgaulin.com"


from gmusicapi import Webclient, Musicmanager
from gmusicapi.clients import OAUTH_FILEPATH
import mutagen
import json
import os
import time
import re
from getpass import getpass
from httplib import BadStatusLine, CannotSendRequest

MAX_UPLOAD_ATTEMPTS_PER_FILE = 3
MAX_CONNECTION_ERRORS_BEFORE_QUIT = 5
STANDARD_SLEEP = 5
MAX_SONGS_IN_PLAYLIST = 1000
LOCAL_OAUTH_FILE = './oauth.cred'

class MusicSync(object):
    def __init__(self, email=None, password=None):
        self.mm = Musicmanager()
        self.wc = Webclient()
        if not email:
            email = raw_input("Email: ")
        if not password:
            password = getpass()

        self.email = email
        self.password = password

        self.logged_in = self.auth()

        print "Fetching playlists from Google..."
        self.playlists = self.wc.get_all_playlist_ids(auto=False)
        print "Got %d playlists." % len(self.playlists['user'])
        print ""


    def auth(self):
        self.logged_in = self.wc.login(self.email, self.password)
        if not self.logged_in:
            print "Login failed..."
            exit()

        print ""
        print "Logged in as %s" % self.email
        print ""

        if not os.path.isfile(OAUTH_FILEPATH):
            print "First time login. Please follow the instructions below:"
            self.mm.perform_oauth()
        self.logged_in = self.mm.login()
        if not self.logged_in:
            print "OAuth failed... try deleting your %s file and trying again." % OAUTH_FILEPATH
            exit()

        print "Authenticated"
        print ""


    def sync_playlist(self, artist_title_array, playlist_title = -99):
        if playlist_title == -99:
            title = "GMusicSync Playlist %3d"%time.time()
        else: title = str(playlist_title)
        print "Synching playlist: %s" % title
        if title not in self.playlists['user']:
            print "   didn't exist... creating..."
            self.playlists['user'][title] = [self.wc.create_playlist(title)]
        print ""

        plid = self.playlists['user'][title][0]
        goog_songs = self.wc.get_playlist_songs(plid)
        print "%d songs already in Google Music playlist" % len(goog_songs)
        pc_songs = artist_title_array
        print "%d songs in local playlist" % len(pc_songs)

        # Sanity check max 1000 songs per playlist
        if len(pc_songs) > MAX_SONGS_IN_PLAYLIST:
            print "    Google music doesn't allow more than %d songs in a playlist..." % MAX_SONGS_IN_PLAYLIST
            print "    Will only attempt to sync the first %d songs." % MAX_SONGS_IN_PLAYLIST
            del pc_songs[MAX_SONGS_IN_PLAYLIST:]

        existing_files = 0
        added_files = 0
        failed_files = 0
        removed_files = 0
        fatal_count = 0

        for fn in pc_songs:
            if self.file_already_in_list(fn, goog_songs):
                existing_files += 1
                continue
            print ""
            try:
                print "Adding: %s - %s"%(fn[0],fn[1])
            except:
                print "Incorrect format for %r, expecting ('artist','title')"%fn
                continue
            online = self.find_song(fn)
            song_id = None
            if online:
                song_id = online['id']
                print "   already uploaded [%s]" % song_id
            else:
                print "   Sorry, can't find song."

            if not song_id:
                failed_files += 1
                continue

            added = self.wc.add_songs_to_playlist(plid, song_id)
            time.sleep(.3) # Don't spam the server too fast...
            print "   done adding to playlist"
            added_files += 1

        print ""
        print "---"
        print "%d songs unmodified" % existing_files
        print "%d songs added" % added_files
        print "%d songs failed" % failed_files
        print "%d songs removed" % removed_files


    def get_files_from_playlist(self, filename):
        files = []
        f = codecs.open(filename, encoding='utf-8')
        for line in f:
            line = line.rstrip().replace(u'\ufeff',u'')
            if line == "" or line[0] == "#":
                continue
            path  = os.path.abspath(self.get_platform_path(line))
            if not os.path.exists(path):
                print "File not found: %s" % line
                continue
            files.append(path)
        f.close()
        return files

    def file_already_in_list(self, artist_title, goog_songs):
        i = 0
        while i < len(goog_songs):
            if self.song_compare(goog_songs[i], artist_title):
                goog_songs.pop(i)
                return True
            i += 1
        return False

    def find_song(self, artist_title):
        try:
            artist = artist_title[0]
            title = artist_title[1]
        except: return None
        results = self.wc.search(title)
        print "\t",results[:2]
        for r in results['song_hits']:
            if self.song_compare(r, artist_title):
                return r
        return None

    def song_compare(self, g_song, artist_title):
        try:
            artist = artist_title[0]
            title = artist_title[1]
        except: return False
        # TODO: add fuzzy matching
        return g_song['title'].lower() == title.lower() and\
               g_song['artist'].lower() == artist.lower()

    def get_platform_path(self, full_path):
        # Try to avoid messing with the path if possible
        if os.sep == '/' and '\\' not in full_path:
            return full_path
        if os.sep == '\\' and '\\' in full_path:
            return full_path
        if '\\' not in full_path:
            return full_path
        return os.path.normpath(full_path.replace('\\', '/'))
