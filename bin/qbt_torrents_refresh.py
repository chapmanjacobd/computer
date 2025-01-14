#!/usr/bin/python3
import time

import qbittorrentapi
from library.utils import devices

qb = qbittorrentapi.Client(host='127.0.0.1', port=8080)

torrents = qb.torrents_info('stalled_downloading')
torrents = [t for t in torrents if t.num_leechs == 0 and t.num_seeds == 0]

error_torrents = []
restart_torrents = []
for t in torrents:
    errors = [tr.msg for tr in qb.torrents_trackers(t.infohash_v2 or t.infohash_v1)]
    if any("torrent not found in your history" in s.lower() for s in errors):
        error_torrents.append(t)
    elif any("slot limit" in s.lower() for s in errors):
        restart_torrents.append(t)

for torrent in error_torrents:
    print(torrent.comment)


torrent_hashes = [t.infohash_v2 or t.infohash_v1 for t in restart_torrents]
if restart_torrents:
    qb.torrents_pause(torrent_hashes=torrent_hashes)
    time.sleep(15)
    qb.torrents_resume(torrent_hashes=torrent_hashes)


torrent_hashes = [t.infohash_v2 or t.infohash_v1 for t in error_torrents]
qb.torrents_pause(torrent_hashes=torrent_hashes)

if error_torrents and devices.confirm("Continue?"):
    qb.torrents_resume(torrent_hashes=torrent_hashes)
