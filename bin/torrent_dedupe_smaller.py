#!/usr/bin/python3

import os
from pathlib import Path

from torrentool.api import Torrent
from xklb.utils import argparse_utils

parser = argparse_utils.ArgumentParser()
parser.add_argument('paths', nargs='+', help='Path(s) to torrent files')
parser.add_argument('-r', '--remove', action='store_true', help='Actually remove files')
args = parser.parse_args()

for torrent_file in args.paths:
    torrent_file = Path(torrent_file)
    if torrent_file.stem.endswith('_2'):
        original_file = torrent_file.with_name(torrent_file.name.replace('_2', ''))
        if original_file.exists():
            torrent1 = Torrent.from_file(original_file)
            torrent2 = Torrent.from_file(torrent_file)
            if sum(f.length for f in torrent1.files) < sum(f.length for f in torrent2.files):
                if args.remove:
                    os.remove(torrent_file)
                else:
                    print(torrent_file)
            else:
                if args.remove:
                    os.remove(original_file)
                else:
                    print(original_file)
