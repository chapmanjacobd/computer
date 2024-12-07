#!/usr/bin/python3
from xklb.mediafiles import torrents_start
from xklb.utils import arggroups, argparse_utils, printing, processes, strings

parser = argparse_utils.ArgumentParser()
arggroups.qBittorrent(parser)
arggroups.debug(parser)

parser.add_argument('search_terms', nargs='+', help="The info_hash, name, or save_path substring to search for")
args = parser.parse_args()

qbt_client = torrents_start.start_qBittorrent(args)
torrents = qbt_client.torrents_info()

torrents = [t for t in torrents if strings.glob_match(args.search_terms, [t.name, t.save_path, t.hash])]

if not torrents:
    processes.no_media_found()

torrents = sorted(torrents, key=lambda t: -t.time_active)
for torrent in torrents:
    print(torrent.name)
    printing.extended_view(torrent.files)
