#!/usr/bin/python3
from library.mediafiles import torrents_start
from library.utils import arggroups, argparse_utils, strings


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

torrents = sorted(torrents, key=lambda x: x.remaining)
for t in torrents:
    print('\t'.join([t.name, strings.file_size(t.remaining)]))
