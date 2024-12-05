#!/usr/bin/python3
import qbittorrentapi
from xklb.utils import devices

qb = qbittorrentapi.Client(host='127.0.0.1', port=8080)

torrents = qb.torrents_info('stalled_downloading')
torrents = [t for t in torrents if t.num_leechs == 0 and t.num_seeds == 0]

error_torrents = []
for t in torrents:
    errors = [tr.msg for tr in qb.torrents_trackers(t.infohash_v2 or t.infohash_v1)]
    if any("torrent not found in your history" in s.lower() for s in errors):
        error_torrents.append(t)

if not error_torrents:
    print("No torrents found with the specified tracker error.")
    exit(0)

for torrent in error_torrents:
    print(torrent.comment)

torrent_hashes = [t.infohash_v2 or t.infohash_v1 for t in error_torrents]
qb.torrents_pause(torrent_hashes=torrent_hashes)

if devices.confirm("Press Enter to resume"):
    qb.torrents_resume(torrent_hashes=torrent_hashes)
