#!/usr/bin/python3

from pathlib import Path

from rich import inspect
from torrentool.api import Torrent
from library.utils import argparse_utils, strings
from library.utils.printing import print_overwrite

parser = argparse_utils.ArgumentParser()
parser.add_argument('paths', nargs='+', help='Path(s) to torrent files')
args = parser.parse_args()

torrents = [
    (torrent_file, Torrent.from_file(torrent_file))
    for torrent_folder in args.paths
    for torrent_file in Path(torrent_folder).glob('*.torrent')
]

len_torrents = len(torrents)
duplicates = {}
for i in range(len_torrents):
    torrent_path1 = torrents[i][0]
    torrent1 = torrents[i][1]

    print_overwrite('Checking', i, 'of', len_torrents, f"({strings.percent(i/len_torrents)})")
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
            lengths_set1 = set(f1.length for f1 in torrent1.files)
            lengths_set2 = set(f2.length for f2 in torrent2.files)
            overlap_lengths = lengths_set1.intersection(lengths_set2)
            match_count = len(overlap_lengths)

            similarity = match_count / len(torrent1.files)
            if similarity > 0.3:
                print(torrent_path1, torrent_path2, 'are similar', strings.percent(similarity))
                inspect(torrent1)
                inspect(torrent2)

        if is_dupe:
            inspect(torrent1)
            inspect(torrent2)

            if torrent_path1 not in duplicates:
                duplicates[torrent_path1] = []
            duplicates[torrent_path1].append(str(torrent_path1))
            duplicates[torrent_path1].append(str(torrent_path2))

print(f"Duplicate groups ({len(duplicates)}):")
for group in sorted(duplicates, key=len, reverse=True):
    print(duplicates[group])
