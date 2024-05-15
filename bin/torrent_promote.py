#!/usr/bin/python3

import argparse
import shutil
import statistics
from pathlib import Path
from typing import List, Tuple

import humanize
from torrentool.api import Torrent
from xklb.utils import arggroups


def sort_and_move_torrents(args):
    paths: List[Path] = []
    for p in args.paths:
        p = Path(p)
        if p.is_dir():
            paths.extend(p.glob("*.torrent"))
        else:
            paths.append(p)

    torrent_data: List[Tuple[Path, float]] = []
    for torrent_file in paths:
        torrent = Torrent.from_file(torrent_file)

        if args.ext and not set(args.ext).intersection(Path(f.name).suffix[1:] for f in torrent.files):
            continue

        file_sizes = [f.length for f in torrent.files]
        if args.average:
            torrent_data.append((torrent_file, statistics.mean(file_sizes)))
        elif args.median:
            torrent_data.append((torrent_file, statistics.median(file_sizes)))
        elif args.file_count:
            torrent_data.append((torrent_file, len(file_sizes)))
        else:
            torrent_data.append((torrent_file, sum(file_sizes)))

    sorted_torrents = sorted(torrent_data, key=lambda x: x[1], reverse=args.reverse)

    for torrent_file, size in sorted_torrents[: args.n]:
        if args.out:
            destination_path = Path(args.out) / torrent_file.name
        else:
            destination_path = torrent_file.parent / '..' / 'start' / torrent_file.name

        if args.dry_run or args.print:
            print('mv', torrent_file, ' ', destination_path, '# ', size if args.file_count else humanize.naturalsize(size, binary=True))
        else:
            shutil.move(torrent_file, destination_path)
            print(destination_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--out', '-o')
    parser.add_argument('-n', type=int, default=20, help='Number of torrents to move')

    parser.add_argument('--reverse', '-r', action='store_true')
    parser.add_argument('--file-count', '--count', action='store_true')
    parser.add_argument(
        '--average', '--avg', '--priority', action='store_true', help='Priority mode: sort by average file size'
    )
    parser.add_argument('--median', '--mid', action='store_true', help='Sort by median file size instead of total size')
    arggroups.debug(parser)

    arggroups.paths_or_stdin(parser)
    args = parser.parse_args()

    if args.out:
        Path(args.out).mkdir(exist_ok=True, parents=True)

    sort_and_move_torrents(args)
