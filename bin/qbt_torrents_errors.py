#!/usr/bin/python3

from library.mediafiles import torrents_start
from library.playback import torrents_info
from library.utils import arggroups, argparse_utils, consts, iterables, printing, strings


def parse_args():
    parser = argparse_utils.ArgumentParser()
    arggroups.qBittorrent(parser)
    arggroups.qBittorrent_torrents(parser)
    arggroups.debug(parser)

    args = parser.parse_args()
    arggroups.args_post(args, parser)

    arggroups.qBittorrent_torrents_post(args)

    return args


def torrents_status():
    args = parse_args()

    def shorten(s, width):
        return s if args.verbose >= consts.LOG_INFO else strings.shorten(s, width)

    qbt_client = torrents_start.start_qBittorrent(args)
    torrents = qbt_client.torrents_info()
    torrents_info.qbt_enhance_torrents(qbt_client, torrents)

    torrents = torrents_info.filter_torrents(args, torrents)

    error_torrents = [t for t in torrents if t.state_enum.is_errored]
    error_torrents = sorted(
        error_torrents, key=lambda t: (t.amount_left == t.total_size, t.eta, t.amount_left), reverse=True
    )
    if error_torrents:
        print("Error Torrents")
        tbl = [
            {
                "state": t.state,
                "name": shorten(t.name, width=40),
                "progress": strings.percent(t.progress),
                "eta": strings.duration_short(t.eta) if t.eta < 8640000 else None,
                "remaining": strings.file_size(t.amount_left) if t.amount_left > 0 else None,
                "files": len(torrents_info.torrent_files(t)) if args.file_counts else None,
                "tracker_msg": "; ".join(msg for _tr, msg in torrents_info.get_error_messages(t)),
                "path": t.content_path if args.verbose >= consts.LOG_INFO else None,
            }
            for t in error_torrents
        ]
        printing.table(iterables.list_dict_filter_bool(tbl))
        print()
