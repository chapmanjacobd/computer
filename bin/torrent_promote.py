#!/usr/bin/python3

import shutil
import statistics
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List
from urllib.parse import urlparse

import humanize
from torrentool.api import Torrent
from library.utils import arggroups, argparse_utils, iterables
from library.utils.log_utils import log

IGNORE_DOMAINS = []
PORN_DOMAINS = [
    'bitporn.eu',
    'exoticaz.to',
    'scenetime.com',
    'superbits.org',
    'pussytorrents.org',
    'happyfappy.org',
    'plab.site',
    'empornium.is',
    'empornium.sx',
]


def get_tracker_dirname(torrent: Torrent):
    if torrent.announce_urls is None:
        return torrent.source

    log.debug(torrent.announce_urls)

    for tracker in iterables.flatten(torrent.announce_urls):
        url = urlparse(tracker)
        domain = '.'.join(url.netloc.rsplit(':')[0].rsplit('.', 2)[-2:]).lower()
        if domain not in IGNORE_DOMAINS:
            if domain in PORN_DOMAINS:
                return ''.join(['porn/', domain])
            else:
                return ''.join(['seed/', domain])

    return torrent.source


def extract_torrent_file(args, torrent_file):
    torrent = Torrent.from_file(torrent_file)

    if args.ext and not set(args.ext).intersection(Path(f.name).suffix[1:] for f in torrent.files):
        return None  # Skip file

    file_sizes = [f.length for f in torrent.files]
    if args.average:
        torrent_size = statistics.mean(file_sizes)
    elif args.median:
        torrent_size = statistics.median(file_sizes)
    elif args.file_count:
        torrent_size = len(file_sizes)
    else:
        torrent_size = sum(file_sizes)

    if args.out:
        dir_name = Path(args.out)
    else:
        dir_name = torrent_file.parent / '..' / 'start'

    if args.tracker_dirnames:
        tracker = get_tracker_dirname(torrent)
        if tracker:
            dir_name /= tracker
    destination_path = dir_name / torrent_file.name

    return (torrent_file, destination_path.resolve(), torrent_size)


def sort_and_move_torrents(args):
    paths: List[Path] = []
    for p in args.paths:
        p = Path(p)
        if p.is_dir():
            paths.extend(p.glob("*.torrent"))
        else:
            paths.append(p)

    with ThreadPoolExecutor() as ex:
        futures = [ex.submit(extract_torrent_file, args, torrent_file) for torrent_file in paths]
    torrent_data = [future.result() for future in futures]
    torrent_data = [data for data in torrent_data if data]

    sorted_torrents = sorted(torrent_data, key=lambda x: x[1], reverse=args.reverse)

    for torrent_file, destination_path, size in sorted_torrents[: args.n]:
        if args.simulate or args.print:
            log.info("%s\t%s", torrent_file, size)
            print(
                'mv',
                torrent_file,
                ' ',
                destination_path,
                '# ',
                size if args.file_count else humanize.naturalsize(size, binary=True),
            )
        else:
            Path(destination_path).parent.mkdir(exist_ok=True, parents=True)
            shutil.move(torrent_file, destination_path)
            print(destination_path)


if __name__ == '__main__':
    parser = argparse_utils.ArgumentParser()
    parser.add_argument('--out', '-o')
    parser.add_argument('-n', type=int, default=20, help='Number of torrents to move')

    parser.add_argument('--tracker-dirnames', '--trackers', action='store_true')
    parser.add_argument('--reverse', '-r', action='store_true')
    parser.add_argument('--file-count', '--count', action='store_true')
    parser.add_argument(
        '--average', '--avg', '--priority', action='store_true', help='Priority mode: sort by average file size'
    )
    parser.add_argument('--median', '--mid', action='store_true', help='Sort by median file size instead of total size')
    arggroups.debug(parser)

    arggroups.paths_or_stdin(parser)
    args = parser.parse_args()
    arggroups.args_post(args, parser)

    sort_and_move_torrents(args)
