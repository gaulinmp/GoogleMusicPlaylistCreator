from musicsync import MusicSync

ms = MusicSync("example@gmail.com","password")
# I use two-factor auth, so the password in my case is a generated "one-time" password

#Dumped output from something like http://groovylists.com/?do=spotify
dump="""Mysterons    Portishead
Tree by the River    Iron & Wine"""
songs = [ (a[1].strip(),a[0].strip()) for a in [s.split("\t") for s in dump.split("\n")]]

ms.sync_playlist(songs)
ms.sync_playlist(songs,playlist_title="Mellow Music")