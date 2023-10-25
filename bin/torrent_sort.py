#!/usr/bin/python3

import argparse
import os
import shutil
from pathlib import Path

from torrentool.api import Torrent


def check_torrents(torrent_folder, files_folder):
    for torrent_file in os.listdir(torrent_folder):
        torrent = Torrent.from_file(os.path.join(torrent_folder, torrent_file))

        all_files_exist = True
        for f in torrent.files:
            if not os.path.exists(os.path.join(files_folder, f.path)):
                all_files_exist = False
                break

        if all_files_exist:
            dest = Path(args.files_folder / '..' / 'complete')
            dest.mkdir(exist_ok=True)
            shutil.move(torrent_file, dest / torrent_file)
        elif any(os.path.exists(os.path.join(files_folder, f.path)) for f in torrent.files):
            dest = Path(args.files_folder / '..' / 'partial')
            dest.mkdir(exist_ok=True)
            shutil.move(torrent_file, dest / torrent_file)
        else:
            dest = Path(args.files_folder / '..' / 'new')
            dest.mkdir(exist_ok=True)
            shutil.move(torrent_file, dest / torrent_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('torrent_folder', help='Folder containing torrent files')
    parser.add_argument('files_folder', help='Folder containing downloaded files')
    args = parser.parse_args()

    check_torrents(args.torrent_folder, args.files_folder)
