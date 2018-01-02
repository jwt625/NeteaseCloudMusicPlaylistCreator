import sqlite3
import json
import codecs
import os

cx = sqlite3.connect(os.path.expanduser('~')+"/AppData/Local/Netease/CloudMusic/Library/webdb.dat")
cx.row_factory = sqlite3.Row
# use local library (including matched) instead of only downloaded
cx2 = sqlite3.connect(os.path.expanduser('~')+"/AppData/Local/Netease/CloudMusic/Library/library.dat")
cx2.row_factory = sqlite3.Row

def getPlaylist():
	cu=cx.cursor()
	cu.execute("select * from web_playlist") 
	playlists=[]
	for item in cu.fetchall():
		playlist=(item["pid"],getPlaylistNameFromJson(item["playlist"]))
		playlists.append(playlist)
	return playlists

def getPlayListMusic(pid):
	cu=cx.cursor()
	cu.execute("select * from web_playlist_track where pid=?",[pid]) 
	musics=[]
	for item in cu.fetchall():
		musics.append(item["tid"]);
	return musics

def getOfflineMusicDetail(tid):
	cu=cx2.cursor()
	cu.execute("select * from track where tid=?",[tid]) 
	music = cu.fetchone()
	if music is None:
		return None
	detail = (music["title"], music["file"])
	return detail


def getOffLineMusicArtist(tid):
	cu=cx2.cursor()
	cu.execute("select * from track where tid=?",[tid]) 
	music = cu.fetchone()
	if music is None:
		return None
	return music["artist"]


def writeArtistToFile(pid, playlistName):
    fname = playlistName.decode('gbk')
    # for windows path format
    forbiddenCh = ['&', ':', '/', '\\', '?', '<', '>', '*', '"']
    for ch in forbiddenCh:
        fname = fname.replace(ch, '_')
    file = codecs.open(fname + "_artist.m3u", "w", "utf-8")
    count = 0
    try:
#		file.writelines("#EXTM3U")
        musicIds, orders = getPlayListMusic(pid)
        for tid in musicIds:
            if tid is not None:
                artist=getOffLineMusicArtist(tid)
                if artist is not None:
                    count=count + 1
                    print(count)
                    file.writelines(u'"'+artist[1:len(artist)-1]+u'",')
    except Exception as e:
        raise
    else:
        pass
    finally:
        file.close()
        if count <= 0:
            os.remove(fname + "_artist.m3u")

def writePlaylistToFile(pid, playlistName):
	fname = playlistName.decode('gbk')
	# for windows path format
	forbiddenCh = ['&', ':', '/', '\\', '?', '<', '>', '*', '"']
	for ch in forbiddenCh:
		fname = fname.replace(ch, '_')

	file = codecs.open(fname + ".m3u", "w", "utf-8")
	count = 0
	try:
		file.writelines("#EXTM3U")
		musicIds = getPlayListMusic(pid)
		for tid in musicIds:
			if tid is not None:
				detail=getOfflineMusicDetail(tid)
				if detail is not None:
					count=count + 1
					file.writelines(u"\n#EXTINF:" + detail[0] + u"\n" + detail[1])
	except Exception as e:
		raise
	else:
		pass
	finally:
		file.close()
		if count <= 0:
			os.remove(fname + ".m3u")

def getPlaylistNameFromJson(jsonStr):
	playlistDetail = json.loads(jsonStr)
	return playlistDetail["name"].encode("GBK", 'ignore');

def getMusicNameFromJson(jsonStr):
	musicDetail = json.loads(jsonStr)
	return musicDetail["name"];

def main():
	playlists = getPlaylist()
	count = 0
	numOfList = 40
	for item in playlists:
		print(item)
		print(item[1].decode('gbk'))
		writePlaylistToFile(item[0], item[1])
		count = count + 1
		if count > numOfList:
			break

if __name__ == '__main__':
	main()
