#!/usr/bin/python3

import argparse
import os
import shutil

from torrentool.api import Torrent


def sort_and_move_torrents(torrent_folder, num_to_move):
    torrent_data = []
    for torrent_file in os.listdir(torrent_folder):
        torrent = Torrent.from_file(os.path.join(torrent_folder, torrent_file))
        total_size = sum(f.length for f in torrent.files)
        torrent_data.append((torrent_file, total_size))

    sorted_torrents = sorted(torrent_data, key=lambda x: x[1])

    for i in range(min(num_to_move, len(sorted_torrents))):
        torrent_file, _ = sorted_torrents[i]
        source_path = os.path.join(torrent_folder, torrent_file)
        destination_path = os.path.join(source_path, '..', 'start', torrent_file)
        shutil.move(source_path, destination_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('torrent_folder', help='Folder containing torrent files')
    parser.add_argument('-n', type=int, default=20, help='Number of torrents to move')
    args = parser.parse_args()

    sort_and_move_torrents(args.torrent_folder, args.n)
