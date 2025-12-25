#!/usr/bin/python3
import os

from library.mediafiles import torrents_start
from library.playback import torrents_info
from library.utils import arggroups, argparse_utils


def parse_args():
    parser = argparse_utils.ArgumentParser()
    arggroups.qBittorrent(parser)
    arggroups.debug(parser)

    arggroups.paths_or_stdin(parser)
    args = parser.parse_args()
    arggroups.args_post(args, parser)
    return args


def normalize(path: str) -> str:
    return os.path.normpath(os.path.realpath(path))


args = parse_args()
input_paths = {normalize(p) for p in args.paths}

qbt_client = torrents_start.start_qBittorrent(args)
torrents = qbt_client.torrents_info()

for t in torrents:
    t_folders = {normalize(p) for p in (t.save_path, t.download_path, t.content_path) if p}

    matched_indexes = []
    for f in torrents_info.torrent_files(t):
        # f.name is relative to the torrent root
        for base in t_folders:
            full_path = normalize(os.path.join(base, f.name))
            if full_path in input_paths:
                matched_indexes.append(f.index)
                break

    if matched_indexes:
        qbt_client.torrents_file_priority(torrent_hash=t.hash, file_ids=matched_indexes, priority=0)
