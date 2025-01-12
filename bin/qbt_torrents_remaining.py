#!/usr/bin/python3
import argparse

from library.mediafiles import torrents_start
from library.playback.torrents_info import qbt_get_tracker
from library.utils import arggroups, argparse_utils, consts, iterables, printing, strings


def parse_args():
    parser = argparse_utils.ArgumentParser()
    arggroups.qBittorrent(parser)
    parser.add_argument(
        "--inactive", "--dead", action=argparse.BooleanOptionalAction, default=False, help="Show inactive torrents"
    )
    arggroups.debug(parser)

    args = parser.parse_args()
    arggroups.args_post(args, parser)
    return args


args = parse_args()

qbt_client = torrents_start.start_qBittorrent(args)

torrents = qbt_client.torrents_info()

torrents = [t for t in torrents if t.state_enum.is_downloading]

torrents = sorted(torrents, key=lambda t: t.amount_left)


def shorten(s, width):
    if len(s) <= width or args.verbose >= consts.LOG_INFO:
        return s
    return s[0:width] + '...'


def gen_row(t):
    d = {
        'name': shorten(t.name, 40),
        'state': t.state,
        'speed': strings.file_size(t.dlspeed) + '/s' if t.dlspeed else None,
        'progress': strings.safe_percent(t.progress),
        'size': strings.file_size(t.total_size),
        'downloaded': strings.file_size(t.downloaded),
        'downloaded_session': strings.file_size(t.downloaded_session),
        'remaining': strings.file_size(t.amount_left),
    }

    if args.verbose >= consts.LOG_INFO:
        d |= {
            'tracker': qbt_get_tracker(qbt_client, t),
            'seen_complete': strings.relative_datetime(t.seen_complete),
            'added_on': strings.relative_datetime(t.added_on),
            'comment': t.comment,
            'content_path': t.content_path,
        }

    return d


printing.table(iterables.conform([gen_row(t) for t in torrents]))
