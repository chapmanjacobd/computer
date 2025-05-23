#!/usr/bin/python3

from pathlib import Path

import humanize
from torrentool.api import Torrent
from library.text import cluster_sort
from library.utils import arggroups, argparse_utils

parser = argparse_utils.ArgumentParser()
parser.add_argument('--small', action='store_true')
parser.add_argument('--size', action='store_true')
parser.add_argument('--only-duplicates', action='store_true')
parser.add_argument('--only-originals', action='store_true')
arggroups.debug(parser)
arggroups.paths_or_stdin(parser)
args = parser.parse_args()

paths = [str(f) for torrent_folder in args.paths for f in Path(torrent_folder).glob('*.torrent')]

groups = cluster_sort.cluster_paths(paths, n_clusters=int(len(paths) / 2.5))
groups = sorted(groups, key=lambda d: (-len(d["grouped_paths"]), -len(d["common_prefix"])))

if not args.only_originals and not args.only_duplicates:
    print("Duplicate groups:")

for group in groups:
    t = [(path, Torrent.from_file(path).total_size) for path in group['grouped_paths']]
    t = sorted(t, key=lambda x: x[1], reverse=not args.small)

    if args.only_originals:
        t = t[:1]
    if args.only_duplicates:
        t = t[1:]

    for path, size in t:
        if args.size:
            print(path, '# ', humanize.naturalsize(size, binary=True))
        else:
            print(path)

    if not args.only_originals and not args.only_duplicates:
        print()
