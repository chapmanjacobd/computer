#!/usr/bin/python3
from collections import defaultdict

import qbittorrentapi
from library.utils import arggroups, argparse_utils


def parse_args():
    parser = argparse_utils.ArgumentParser()
    arggroups.qBittorrent(parser)
    arggroups.debug(parser)

    parser.add_argument('hosts', nargs="+")
    args = parser.parse_args()
    arggroups.args_post(args, parser)
    return args


args = parse_args()

torrents = defaultdict(list)
for host in args.hosts:
    host, port = host.split(':')

    qbt_client = qbittorrentapi.Client(
        host=host,
        port=port,
        username=args.username,
        password=args.password,
    )

    for t in qbt_client.torrents_info():
        torrents[t.hash].append((t.progress, host, port))

for hash, tg in torrents.items():
    if len(tg) == 1:
        continue

    tg = sorted(tg, key=lambda x: x[0], reverse=True)
    for t in tg[1:]:
        progress, host, port = t

        qbt_client = qbittorrentapi.Client(
            host=host,
            port=port,
            username=args.username,
            password=args.password,
        )

        print('Deleting from', host)
        qbt_client.torrents_delete(True, [hash])
