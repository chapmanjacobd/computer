#!/usr/bin/python3

import shutil
from pathlib import Path

from torrentool.api import Torrent
from xklb.utils import argparse_utils


def check_torrents(torrent_folder: Path, files_folder: Path):
    for torrent_file in torrent_folder.glob('*.torrent'):
        torrent = Torrent.from_file(torrent_file)

        no_files_exist = True
        all_files_exist = True
        for f in torrent.files:
            p = files_folder / f.name
            if p.exists() and p.stat().st_size > 0:
                no_files_exist = False
            else:
                all_files_exist = False

        if all_files_exist:
            dest = torrent_folder / '..' / 'complete'
            dest.mkdir(exist_ok=True)
            shutil.move(torrent_file, dest / torrent_file.name)
        elif no_files_exist:
            dest = torrent_folder / '..' / 'new'
            dest.mkdir(exist_ok=True)
            shutil.move(torrent_file, dest / torrent_file.name)
        else:
            dest = torrent_folder / '..' / 'partial'
            dest.mkdir(exist_ok=True)
            shutil.move(torrent_file, dest / torrent_file.name)


if __name__ == '__main__':
    parser = argparse_utils.ArgumentParser()
    parser.add_argument('torrent_folder', help='Folder containing torrent files')
    parser.add_argument('files_folder', help='Folder containing downloaded files')
    args = parser.parse_args()

    torrent_folder = Path(args.torrent_folder)
    files_folder = Path(args.files_folder)
    check_torrents(torrent_folder, files_folder)
