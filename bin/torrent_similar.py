#!/usr/bin/python3

import argparse
import difflib
from pathlib import Path

from torrentool.api import Torrent
from xklb.utils import arggroups, strings
from xklb.utils.log_utils import log
from xklb.utils.printing import print_overwrite

parser = argparse.ArgumentParser()
arggroups.debug(parser)
arggroups.paths_or_stdin(parser)
args = parser.parse_args()

torrents = [
    (torrent_file, Torrent.from_file(torrent_file))
    for torrent_folder in args.paths
    for torrent_file in Path(torrent_folder).glob('*.torrent')
]

log.info('Data loaded')

duplicates:dict[str, list[tuple[str, int]]] = {}
len_torrents = len(torrents)
for i in range(len_torrents):
    torrent1_path = torrents[i][0]
    torrent1 = torrents[i][1]
    torrent1_size = torrents[i][1].total_size

    print_overwrite('Checking', i, 'of', len_torrents, f"({strings.safe_percent(i/len_torrents)})")
    for j in range(i + 1, len(torrents)):
        torrent2_path = torrents[j][0]
        torrent2 = torrents[j][1]
        torrent2_size = torrents[j][1].total_size

        if difflib.SequenceMatcher(None, torrent2_path.name, torrent1_path.name).ratio() > 0.73:
            if torrent1_path not in duplicates:
                duplicates[str(torrent1_path)] = []
            duplicates[str(torrent1_path)].append((str(torrent1_path), torrent1_size))
            duplicates[str(torrent1_path)].append((str(torrent2_path), torrent2_size))

print("Duplicate groups:")
for group in sorted(duplicates, key=len, reverse=True):
    print(sorted(duplicates[group], key=lambda x: x[1], reverse=True))
