Provides a utility class around the Google Music API that allows for easy creation of playlist from artist-title pairs.

##Features
Select a list of songs and this will add them to a playlist:
* Create or modify an existing Google Music playlist
* Add uploaded (or files already online) to playlist

It does not:
* Add songs from all_access (yet)
* Remove songs from playlist
* Remove duplicate entries from playlists
* Re-order playlists (only ensures they contain the same files)

Todo:
* Add adding songs from all_access, which is a TODO on the Unofficial Google Music API

##Usage

```python
from musicsync import MusicSync
ms = MusicSync()
# Will prompt for Email and Password - if 2-factor auth is on you'll need to generate a one-time password
# The first time you use this (or another script that uses gmusicapi) you will be prompted to authenticate via an OAuth browser window - you will need to copy paste the URL (be careful - under Windows sometimes spaces are inserted into the copy/paste at new lines)

# To sync a playlist
ms.sync_playlist( [ ('artist','title') ], playlist_title="Optional Title" )

# To sync a playlist with an automatically generated name
ms.sync_playlist( [ ('artist','title') ] )

```


##Requirements
Requires:
* gmusicapi (can use: pip install gmusicapi - or get it from https://github.com/simon-weber/Unofficial-Google-Music-API)
* avconv (see http://unofficial-google-music-api.readthedocs.org/en/latest/usage.html#usage)

- - -

API used: https://github.com/simon-weber/Unofficial-Google-Music-API

Thanks to: Tom Graham (the originator of the playlist syncing), Kevin Kwok and Simon Weber

Use at your own risk - especially for existing playlists

Free to use, reuse, copy, clone, etc
