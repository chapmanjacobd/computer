#!/usr/bin/python3

import argparse
import difflib
from pathlib import Path

from rich import inspect
from torrentool.api import Torrent
from xklb.utils import arggroups
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

duplicates = {}
for i in range(len(torrents)):
    torrent_path1 = torrents[i][0]
    torrent1 = torrents[i][1]

    for j in range(i + 1, len(torrents)):
        torrent_path2 = torrents[j][0]
        torrent2 = torrents[j][1]

        print_overwrite('Comparing', i, 'with', j)
        if difflib.SequenceMatcher(None, torrent_path2.name, torrent_path1.name).ratio() > 0.73:
            inspect(torrent1)
            inspect(torrent2)

            if torrent_path1 not in duplicates:
                duplicates[torrent_path1] = []
            duplicates[torrent_path1].append(torrent_path1)
            duplicates[torrent_path1].append(torrent_path2)

print("Duplicate groups:")
for group in sorted(duplicates, key=len, reverse=True):
    print(duplicates[group])
