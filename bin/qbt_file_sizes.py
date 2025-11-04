#!/usr/bin/python3
import qbittorrentapi
from library.playback.torrents_info import qbt_get_tracker
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
        try:
            d = {
                'host': host,
                'torrent_name': t.name,
                'total_size': t.total_size,
                'files_sizes': [f.size for f in t.files],
                'tracker': qbt_get_tracker(qbt_client, t),
            }
            torrents.append(d)
        except (qbittorrentapi.APIConnectionError, ConnectionRefusedError):
            log.warning("ConnectionError %s %s getting %s files or tracker", host, port, t.name)


for i in range(len(torrents)):
    for j in range(i + 1, len(torrents)):
        t1 = torrents[i]
        t2 = torrents[j]

        files1 = t1['files_sizes']
        files2 = t2['files_sizes']

        if len(files1) == 0:
            log.warning('Empty torrent %s', t1)
            continue
        if len(files2) == 0:
            log.warning('Empty torrent %s', t2)
            continue

        size_ratio = min(t1['total_size'], t2['total_size']) / max(t1['total_size'], t2['total_size'])
        if size_ratio >= 0.73:
            similarity = iterables.similarity(files1, files2)
            if similarity > 0.50:
                print(similarity)
                print(t1['host'], t1['torrent_name'], t1['tracker'], sep='\t')
                print(t2['host'], t2['torrent_name'], t2['tracker'], sep='\t')
                print()
