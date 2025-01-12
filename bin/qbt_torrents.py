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
    parser.add_argument("--priority", action='store_true', help="Sort by priority")
    arggroups.debug(parser)

    args = parser.parse_args()
    arggroups.args_post(args, parser)
    return args


args = parse_args()

qbt_client = torrents_start.start_qBittorrent(args)

torrents = qbt_client.torrents_info()

torrents = [t for t in torrents if t.state_enum.is_downloading]

if args.priority:
    torrents = sorted(torrents, key=lambda t: t.priority)
elif args.inactive:
    torrents = sorted(torrents, key=lambda t: t.time_active * t.last_activity)
else:
    torrents = sorted(torrents, key=lambda t: t.eta)


def shorten(s, width):
    if len(s) <= width or args.verbose >= consts.LOG_INFO:
        return s
    return s[0:width] + '...'


def gen_row(t):
    is_inactive = t.downloaded_session == 0
    if args.inactive != is_inactive:
        return

    d = {}

    if is_inactive:
        d |= {
            'name': shorten(t.name, 65),
            "num_seeds": f"{t.num_seeds} ({t.num_complete})",
            'progress': strings.safe_percent(t.progress),
            'downloaded': strings.file_size(t.downloaded),
            'remaining': strings.file_size(t.amount_left),
            'state': t.state,
            'time_active': strings.duration(t.time_active),
        }
    else:
        d |= {
            'name': shorten(t.name, 35),
            "num_seeds": f"{t.num_seeds} ({t.num_complete})",
            'progress': strings.safe_percent(t.progress),
            'remaining': strings.file_size(t.amount_left),
            'speed': strings.file_size(t.dlspeed) + '/s' if t.dlspeed else None,
            'eta': strings.duration(t.eta),
            'downloaded_session': strings.file_size(t.downloaded_session),
        }

    if args.verbose >= consts.LOG_INFO:
        d |= {
            'tracker': qbt_get_tracker(qbt_client, t),
            'seen_complete': strings.relative_datetime(t.seen_complete),
            'added_on': strings.relative_datetime(t.added_on),
            'last_activity': strings.relative_datetime(t.last_activity),
            'size': strings.file_size(t.total_size),
            'comment': t.comment,
            'content_path': t.content_path,
        }

    return d


printing.table(iterables.conform([gen_row(t) for t in torrents]))
