#!/usr/bin/python3
from xklb.mediafiles import torrents_start
from xklb.utils import arggroups, argparse_utils, printing, processes, strings

parser = argparse_utils.ArgumentParser()
arggroups.qBittorrent(parser)
arggroups.capability_soft_delete(parser)
arggroups.capability_delete(parser)
arggroups.debug(parser)

parser.add_argument('search_terms', nargs='+', help="The info_hash, name, or save_path substring to search for")
args = parser.parse_args()

qbt_client = torrents_start.start_qBittorrent(args)
torrents = qbt_client.torrents_info()

torrents = [t for t in torrents if strings.glob_match(args.search_terms, [t.name, t.save_path, t.hash])]

if not torrents:
    processes.no_media_found()

torrents = sorted(torrents, key=lambda t: -t.time_active)
printing.extended_view(torrents)

torrent_hashes = [t.hash for t in torrents]
if args.mark_deleted:
    qbt_client.torrents_add_tags(tags="xklb-delete", torrent_hashes=torrent_hashes)
elif args.delete_files:
    qbt_client.torrents_delete(delete_files=True, torrent_hashes=torrent_hashes)
elif args.delete_rows:
    qbt_client.torrents_delete(delete_files=False, torrent_hashes=torrent_hashes)
