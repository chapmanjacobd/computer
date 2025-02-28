#!/usr/bin/python3
import time

from library.mediafiles import torrents_start
from library.utils import arggroups, argparse_utils, devices


def parse_args():
    parser = argparse_utils.ArgumentParser()
    arggroups.qBittorrent(parser)
    arggroups.debug(parser)

    args = parser.parse_args()
    arggroups.args_post(args, parser)
    return args


args = parse_args()

qbt_client = torrents_start.start_qBittorrent(args)
torrents = qbt_client.torrents_info()
torrents = [t for t in torrents if not t.state_enum.is_complete and t.num_leechs == 0 and t.num_seeds == 0]

error_torrents = []
restart_torrents = []
for t in torrents:
    errors = [tr.msg for tr in qbt_client.torrents_trackers(t.hash)]
    if any("torrent not found in your history" in s.lower() for s in errors):
        error_torrents.append(t)
    elif any("slot limit" in s.lower() for s in errors):
        restart_torrents.append(t)

for torrent in error_torrents:
    print(torrent.comment)


torrent_hashes = [t.hash for t in restart_torrents]
if restart_torrents:
    qbt_client.torrents_pause(torrent_hashes=torrent_hashes)
    time.sleep(15)
    qbt_client.torrents_resume(torrent_hashes=torrent_hashes)


torrent_hashes = [t.hash for t in error_torrents]
qbt_client.torrents_pause(torrent_hashes=torrent_hashes)

if error_torrents and devices.confirm("Continue?"):
    qbt_client.torrents_resume(torrent_hashes=torrent_hashes)
