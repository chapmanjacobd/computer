#!/usr/bin/python3
import sys
import time

from library.mediafiles import torrents_start
from library.utils import arggroups, argparse_utils


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

MAX_RETRIES = 1
error_torrents = []
restart_torrents = []
for t in torrents:
    errors = []
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            errors = [tr.msg for tr in qbt_client.torrents_trackers(t.hash)]
            break
        except Exception as e:
            if attempt >= MAX_RETRIES:
                print(f"Failed to get trackers after {attempt} attempts:", t.name, file=sys.stderr)
            time.sleep(2)

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

if error_torrents:
    qbt_client.torrents_add_tags('library-refresh', torrent_hashes=torrent_hashes)
