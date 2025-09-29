#!/usr/bin/python3

from concurrent.futures import ThreadPoolExecutor

import libtorrent as lt
import torrent_info
from library.utils import arggroups, argparse_utils

parser = argparse_utils.ArgumentParser()
parser.add_argument("--allowed", nargs='+', default=[])
arggroups.debug(parser)
parser.add_argument('paths', nargs='+', help='Path(s) to torrent files')
args = parser.parse_args()

allowed = {t.encode('utf-8') for t in args.allowed}


def remove_trackers(path):
    with open(path, 'rb') as f:
        torrent_data = lt.bdecode(f.read())

    if b'announce-list' in torrent_data:
        filtered_announce_list = []
        for tier in torrent_data[b'announce-list']:
            new_tier = [tracker_url for tracker_url in tier if tracker_url in allowed]
            if new_tier:
                filtered_announce_list.append(new_tier)

        torrent_data[b'announce-list'] = filtered_announce_list

    if b'announce' in torrent_data:
        if torrent_data[b'announce'] not in allowed:
            del torrent_data[b'announce']

    with open(path, 'wb') as f:
        f.write(lt.bencode(torrent_data))


torrent_files = list(torrent_info.gen_torrents(args.paths))
with ThreadPoolExecutor(max_workers=1) as executor:
    futures = [executor.submit(remove_trackers, f) for f in torrent_files]
    for future in futures:
        future.result()
