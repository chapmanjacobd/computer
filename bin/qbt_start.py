#!/usr/bin/python3

from library.mediafiles import torrents_start
from library.playback.torrents_info import qbt_get_tracker
from library.utils import arggroups, argparse_utils


def parse_args():
    parser = argparse_utils.ArgumentParser()
    arggroups.qBittorrent(parser)
    parser.add_argument("--recheck", action="store_true", help="Recheck the torrents instead of starting them.")
    arggroups.debug(parser)

    args = parser.parse_args()
    arggroups.args_post(args, parser)
    return args


args = parse_args()

qbt_client = torrents_start.start_qBittorrent(args)

torrents = qbt_client.torrents_info()
torrents = [t for t in torrents if t.state == 'error']

if not torrents:
    exit()

for t in torrents:
    msg = '; '.join(tr.msg for tr in torrents[0].trackers if tr.msg != 'This torrent is private')
    tracker = qbt_get_tracker(qbt_client, t)
    print('\t'.join([tracker, msg, t.content_path]))

torrent_hashes = [torrent.hash for torrent in torrents]

if args.recheck:
    qbt_client.torrents_recheck(torrent_hashes=torrent_hashes)
else:
    qbt_client.torrents_resume(torrent_hashes=torrent_hashes)
