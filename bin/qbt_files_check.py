#!/usr/bin/python3
import os.path
from collections import defaultdict
from pathlib import Path

from library.mediafiles import torrents_start
from library.utils import arggroups, argparse_utils, file_utils


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

fs_folders = set()
fs_files = set()

known = defaultdict(int)
for t in torrents:
    t_folders = [t.save_path, t.download_path, t.content_path]
    t_folders = [os.path.realpath(s) for s in t_folders]

    for t_folder in t_folders:
        if Path(t_folder).exists():
            if Path(t_folder).is_file():
                fs_files.add(t_folder)
            elif t_folder not in fs_folders:
                fs_folders.add(t_folder)
                folder_files, _, _ = file_utils.rglob(t_folder, quiet=True)
                fs_files |= folder_files

    t_folder_count = defaultdict(int)
    for t_folder in t_folders:
        for f in t.files:
            p = os.path.join(t_folder, f.name)
            if p in fs_files:
                known[p] += 1
                t_folder_count[t_folder] += 1

    if len(t_folder_count) > 1:
        print(t.name, t_folder_count)

duplicates = [p for p, count in known.items() if count > 1]
if duplicates:
    print('DUPLICATES')
    print(duplicates)
    print()

orphans = fs_files - set(known.keys())
if orphans:
    print('ORPHANS')
    print(orphans)
    print()
