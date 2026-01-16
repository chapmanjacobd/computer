#!/usr/bin/python3
import qbittorrentapi
from library.mediafiles import torrents_start
from library.playback import torrents_info
from library.utils import arggroups, argparse_utils, strings
from library.utils.log_utils import log


def parse_args():
    parser = argparse_utils.ArgumentParser()
    arggroups.qBittorrent(parser)
    arggroups.debug(parser)

    args = parser.parse_args()
    arggroups.args_post(args, parser)
    return args


def is_trumped_torrent(t):
    for tr, msg in torrents_info.get_error_messages(t):
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
                'torrent not registered',
                'infohash not found',
                'has been deleted',
                'torrent deleted',
                'no record found',
                'not authorized for use with this tracker',
                'not registered or allowed on this tracker',
            ]
        ):
            print(strings.percent(t.progress), t.name)
            print('     ', msg, tr["url"])
            print('     ', t.comment)
            return True

    return False


args = parse_args()

qbt_client = torrents_start.start_qBittorrent(args)
torrents = qbt_client.torrents_info()

for t in torrents:
    try:
        is_trumped = is_trumped_torrent(t)
        if is_trumped:
            qbt_client.torrents_add_tags(['library-trumped'], torrent_hashes=[t.hash])

    except (qbittorrentapi.APIConnectionError, ConnectionRefusedError):
        log.error("ConnectionError: skipping %s", t.name)
