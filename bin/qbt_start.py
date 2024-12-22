#!/usr/bin/python3
import argparse

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

parser = argparse.ArgumentParser()
parser.add_argument("--recheck", action="store_true", help="Recheck the torrents instead of starting them.")
args = parser.parse_args()

torrents = qbt_client.torrents_info()
torrents = [t.state == 'error' for t in torrents]

if not torrents:
    exit()

raise
# TODO print error reasons

torrent_hashes = [torrent.hash for torrent in torrents]

if args.recheck:
    qbt_client.torrents_recheck(torrent_hashes=torrent_hashes)
else:
    qbt_client.torrents_resume(torrent_hashes=torrent_hashes)
