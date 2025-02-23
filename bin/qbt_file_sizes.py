#!/usr/bin/python3
import qbittorrentapi
from library.utils import arggroups, argparse_utils, iterables
from library.utils.log_utils import log


def parse_args():
    parser = argparse_utils.ArgumentParser()
    arggroups.qBittorrent(parser)
    arggroups.debug(parser)

    parser.add_argument('hosts', nargs="+")
    args = parser.parse_args()
    arggroups.args_post(args, parser)
    return args


args = parse_args()

torrents = []
for host in args.hosts:
    host, port = host.split(':')

    qbt_client = qbittorrentapi.Client(
        host=host,
        port=port,
        username=args.username,
        password=args.password,
    )

    for t in qbt_client.torrents_info():
        torrents.append({'host': host, 'torrent_name': t.name, 'files_sizes': [f.size for f in t.files]})


comparison_results = []
for i in range(len(torrents)):
    for j in range(i + 1, len(torrents)):
        torrent1 = torrents[i]
        torrent2 = torrents[j]

        files1 = torrent1['files_sizes']
        files2 = torrent2['files_sizes']

        len1 = len(files1)
        len2 = len(files2)

        if len1 == 0:
            log.warning('Empty torrent %s', torrent1)
            continue
        if len2 == 0:
            log.warning('Empty torrent %s', torrent2)
            continue

        ratio = min(len1, len2) / max(len1, len2)
        if ratio >= 0.9:  # 10% tolerance
            similarity = iterables.similarity(files1, files2)
            if similarity > 0.73:
                comparison_results.append(
                    {
                        't1': torrent1,
                        't2': torrent2,
                    }
                )
