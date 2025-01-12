#!/usr/bin/python3

from collections import Counter

from library.mediafiles import torrents_start
from library.playback.torrents_info import qbt_get_tracker
from library.utils import arggroups, argparse_utils, consts, iterables, printing, strings


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

torrents = [t for t in torrents if t.state == "missingFiles"]
torrents = sorted(torrents, key=lambda t: t.time_active * t.last_activity)


def shorten(s, width):
    if len(s) <= width or args.verbose >= consts.LOG_INFO:
        return s
    return s[0:width] + '...'


def gen_row(t):
    d = {
        'tracker': qbt_get_tracker(qbt_client, t),
        'name': shorten(t.name, 65),
        'completed_on': strings.relative_datetime(t.completion_on),
        'time_active': strings.duration(t.time_active),
        'seen_complete': strings.relative_datetime(t.seen_complete),
        'added_on': strings.relative_datetime(t.added_on),
        'last_activity': strings.relative_datetime(t.last_activity),
        'size': strings.file_size(t.total_size),
        'downloaded': strings.file_size(t.downloaded),
        'files': dict(Counter(strings.safe_percent(f.progress) for f in t.files)),
        'comment': t.comment,
        'content_path': t.content_path,
    }

    return d


printing.table(iterables.conform([gen_row(t) for t in torrents]))
