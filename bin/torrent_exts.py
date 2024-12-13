#!/usr/bin/python3

from collections import Counter
from pathlib import Path

from torrentool.api import Torrent
from library.utils import arggroups, argparse_utils


def print_exts(args):
    paths: list[Path] = []
    for p in args.paths:
        p = Path(p)
        if p.is_dir():
            paths.extend(p.glob("*.torrent"))
        else:
            paths.append(p)

    exts = Counter()
    for torrent_file in paths:
        torrent = Torrent.from_file(torrent_file)
        for f in torrent.files:
            exts[Path(f.name).suffix] += 1

    print(exts)


if __name__ == '__main__':
    parser = argparse_utils.ArgumentParser()
    arggroups.debug(parser)

    arggroups.paths_or_stdin(parser)
    args = parser.parse_args()

    print_exts(args)
