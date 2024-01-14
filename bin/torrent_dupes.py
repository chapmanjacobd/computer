#!/usr/bin/python3

import argparse
from pathlib import Path

from torrentool.api import Torrent
from xklb.utils import strings
from rich import inspect

parser = argparse.ArgumentParser()
parser.add_argument('paths', nargs='+', help='Path(s) to torrent files')
args = parser.parse_args()

torrents = [
    (torrent_file, Torrent.from_file(torrent_file))
    for torrent_folder in args.paths
    for torrent_file in Path(torrent_folder).glob('*.torrent')
]

duplicates = {}
for i in range(len(torrents)):
    torrent_path1 = torrents[i][0]
    torrent1 = torrents[i][1]

    for j in range(i + 1, len(torrents)):
        torrent_path2 = torrents[j][0]
        torrent2 = torrents[j][1]

        is_dupe = False
        if torrent1.files == torrent2.files:
            is_dupe = True
        elif len(torrent1.files) > 3 and len(torrent1.files) == len(torrent2.files):
            sizes1 = [f.length for f in torrent1.files]
            sizes2 = [f.length for f in torrent2.files]
            if sizes1 == sizes2:
                is_dupe = True

        elif len(torrent1.files) > 10 and len(torrent2.files) > 10:
            match_count = 0
            for f1, f2 in zip(torrent1.files, torrent2.files):
                if f1.length == f2.length:
                    match_count += 1
            similarity = match_count / len(torrent1.files)
            if similarity > 0.3:
                print(torrent_path1, torrent_path2, 'are similar', strings.safe_percent(similarity))
                inspect(torrent1)
                inspect(torrent2)

        if is_dupe:
            inspect(torrent1)
            inspect(torrent2)

            if torrent_path1 not in duplicates:
                duplicates[torrent_path1] = []
            duplicates[torrent_path1].append(torrent_path1)
            duplicates[torrent_path1].append(torrent_path2)

print("Duplicate groups:")
for group in sorted(duplicates, key=len, reverse=True):
    print(duplicates[group])
