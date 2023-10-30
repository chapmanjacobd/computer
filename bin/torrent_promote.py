#!/usr/bin/python3

import argparse
import shutil
from pathlib import Path

import humanize
from torrentool.api import Torrent


def sort_and_move_torrents(args):
    torrent_folder = Path(args.torrent_folder)

    torrent_data = []
    for torrent_file in args.paths or torrent_folder.glob('*.torrent'):
        torrent = Torrent.from_file(torrent_file)
        total_size = sum(f.length for f in torrent.files)
        torrent_data.append((torrent_file, total_size))

    sorted_torrents = sorted(torrent_data, key=lambda x: x[1], reverse=args.reverse)

    for torrent_file, size in sorted_torrents[: args.n]:
        destination_path = torrent_folder / '..' / 'start' / torrent_file.name

        if args.dry_run:
            print('mv', torrent_file, ' ', destination_path, '# ', humanize.naturalsize(size, binary=True))
        else:
            shutil.move(torrent_file, destination_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('torrent_folder', help='Folder containing torrent files')
    parser.add_argument('-n', type=int, default=20, help='Number of torrents to move')
    parser.add_argument('--reverse', '-r', action='store_true')
    parser.add_argument('--dry-run', '-p', action='store_true')
    parser.add_argument('paths', nargs='*')
    args = parser.parse_args()

    sort_and_move_torrents(args)
