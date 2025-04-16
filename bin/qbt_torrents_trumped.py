#!/usr/bin/python3
from library.mediafiles import torrents_start
from library.playback import torrents_info
from library.utils import arggroups, argparse_utils, devices, strings


def parse_args():
    parser = argparse_utils.ArgumentParser()
    arggroups.qBittorrent(parser)
    arggroups.debug(parser)

    args = parser.parse_args()
    arggroups.args_post(args, parser)
    return args


def is_trumped_torrent(t):
    for _tr, msg in torrents_info.get_error_messages(t):
        if any(
            s in msg.lower()
            for s in [
                'not found in your history',
            ]
        ):
            return False

        if any(
            s in msg.lower()
            for s in [
                'invalid torrent',
                'unregistered torrent',
                'torrent not found',
                'infohash not found',
            ]
        ):
            print(t.name, 'error matched', msg)
            return True

    return False


args = parse_args()

qbt_client = torrents_start.start_qBittorrent(args)
torrents = qbt_client.torrents_info()

torrents = [t for t in torrents if is_trumped_torrent(t)]
for t in torrents:
    print(strings.percent(t.progress), t.name, t.comment)
    qbt_client.torrents_add_tags(['library-trumped'], torrent_hashes=[t.hash])
