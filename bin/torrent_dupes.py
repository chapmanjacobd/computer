#!/usr/bin/python3

import argparse
from pathlib import Path

from torrentool.api import Torrent
from xklb.utils import strings

parser = argparse.ArgumentParser()
parser.add_argument('paths', nargs='+', help='Path(s) to torrent files')
args = parser.parse_args()

torrents = [
    (torrent_file, Torrent.from_file(torrent_file))
    for torrent_folder in args.paths
    for torrent_file in Path(torrent_folder).glob('*.torrent')
]

duplicates = []
for i in range(len(torrents)):
    name1 = torrents[i][0]
    torrent1 = torrents[i][1]

    for j in range(i + 1, len(torrents)):
        name2 = torrents[j][0]
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
                print(name1, name2, 'are similar', strings.safe_percent(similarity))

        if is_dupe:
            if name1 not in duplicates:
                duplicates[name1] = []
            duplicates[name1].append(name1)
            duplicates[name1].append(name2)

print("Duplicate groups:")
for group in sorted(duplicates, key=len, reverse=True):
    print(duplicates[group])
