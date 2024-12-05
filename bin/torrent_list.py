#!/usr/bin/python3
import qbittorrentapi
from xklb.utils import arggroups, argparse_utils, iterables, printing, strings

parser = argparse_utils.ArgumentParser()
arggroups.debug(parser)
args = parser.parse_args()

qb = qbittorrentapi.Client(host='127.0.0.1', port=8080)

categories = []
for category in [
    "completed",
    "seeding",
    "stalled_uploading",
    "stalled_downloading",
    "downloading",
    "checking",
    "moving",
    "stopped",
    "errored",
]:
    torrents = qb.torrents_info(category)  # type: ignore
    files = list(iterables.flatten(t.files for t in torrents))
    categories.append(
        {
            'state': category,
            'count': len(torrents),
            'size': strings.file_size(sum(f.size for f in files)),
            'file_count': len(files),
        }
    )
    if 0 < len(torrents) < 50:
        print(category)
        if args.verbose >= 1:
            printing.extended_view(torrents)
        else:
            torrents = sorted(torrents, key=lambda t: (-t.seen_complete, t.time_active))
            printing.table(
                [
                    {
                        'name': t.name,
                        'seen_complete': strings.relative_datetime(t.seen_complete) if t.seen_complete > 0 else None,
                        'last_activity': strings.relative_datetime(t.last_activity),
                        'time_active': strings.duration(t.time_active),
                    }
                    for t in torrents
                ]
            )
            print()

            torrents = sorted(
                torrents, key=lambda t: (t.amount_left == t.total_size, t.eta, t.amount_left), reverse=True
            )
            printing.table(
                [
                    {
                        'name': t.name,
                        'progress': strings.safe_percent(t.progress),
                        'eta': strings.duration(t.eta) if t.eta < 8640000 else None,
                        'remaining': strings.file_size(t.amount_left),
                        'num_seeds': t.num_seeds,
                        # 'num_leechs': t.num_leechs,
                        # 'comment': t.comment,
                    }
                    for t in torrents
                ]
            )
        print()

printing.table(categories)
