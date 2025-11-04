#!/usr/bin/python3
import os
from collections import defaultdict

from library.mediafiles import torrents_start
from library.playback import torrents_info
from library.utils import arggroups, argparse_utils


def parse_args():
    parser = argparse_utils.ArgumentParser()
    parser.add_argument("--folders", action="store_true", help="Group by dirname")
    arggroups.qBittorrent(parser)
    arggroups.debug(parser)

    args = parser.parse_args()
    arggroups.args_post(args, parser)
    return args


args = parse_args()

qbt_client = torrents_start.start_qBittorrent(args)
torrents = qbt_client.torrents_info()

if args.folders:
    for t in torrents:
        folder_groups = defaultdict(list)
        for f in torrents_info.torrent_files(t):
            folder_name = os.path.dirname(f.name)
            folder_groups[folder_name].append(f.size)

        for folder, files_size in folder_groups.items():
            print(sum(files_size), len(files_size), sep='\t')
else:
    for t in torrents:
        print(t.total_size, len(torrents_info.torrent_files(t)), sep='\t')
