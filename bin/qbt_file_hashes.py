#!/usr/bin/python3
from library.mediafiles import torrents_start
from library.utils import arggroups, argparse_utils, printing


def parse_args():
    parser = argparse_utils.ArgumentParser()
    arggroups.qBittorrent(parser)
    arggroups.debug(parser)

    args = parser.parse_args()
    arggroups.args_post(args, parser)
    return args


args = parse_args()

qbt_client = torrents_start.start_qBittorrent(args)
torrents = qbt_client.torrents_info()

for t in torrents:
    printing.pipe_print('\n'.join(f"{f.size}\t{f.name}" for f in t.files))
