#!/usr/bin/python3
from xklb.mediafiles import torrents_start
from xklb.utils import arggroups, argparse_utils, iterables, printing, strings

parser = argparse_utils.ArgumentParser()
arggroups.qBittorrent(parser)
arggroups.debug(parser)
args = parser.parse_args()

qbt_client = torrents_start.start_qBittorrent(args)
all_torrents = qbt_client.torrents_info()

torrents_by_state = {}
for torrent in all_torrents:
    torrents_by_state.setdefault(torrent.state, []).append(torrent)

interesting_states = [
    'stoppedUP',
    'queuedUP',
    'stoppedDL',
    'forcedMetaDL',
    'metaDL',
    'forcedDL',
    'stalledDL',
    # 'forcedUP', 'stalledUP', 'uploading',  # not very interesting
    'downloading',
    'missingFiles',
    'error',
]

tbl = []
for state in interesting_states:
    torrents = torrents_by_state.get(state)
    if not torrents:
        continue

    torrents = sorted(torrents, key=lambda t: (-t.seen_complete, t.time_active))

    if args.verbose >= 1:
        printing.extended_view(torrents)
    else:
        tbl.extend(
            [
                {
                    'state': state,
                    'name': printing.path_fill(t.name, width=76),
                    'seen_complete': strings.relative_datetime(t.seen_complete) if t.seen_complete > 0 else None,
                    'last_activity': strings.relative_datetime(t.last_activity),
                    'time_active': strings.duration(t.time_active),
                }
                for t in torrents
            ]
        )
printing.table(tbl)
print()


tbl = []
for state in interesting_states:
    torrents = torrents_by_state.get(state)
    if not torrents:
        continue

    torrents = sorted(torrents, key=lambda t: (t.amount_left == t.total_size, t.eta, t.amount_left), reverse=True)

    if args.verbose == 0:
        tbl.extend(
            [
                {
                    'state': state,
                    'name': printing.path_fill(t.name, width=76),
                    'progress': strings.safe_percent(t.progress),
                    'eta': strings.duration(t.eta) if t.eta < 8640000 else None,
                    'remaining': strings.file_size(t.amount_left),
                    'num_seeds': f"{t.num_complete} ({t.num_seeds})",
                    # 'num_leechs': f"{t.num_incomplete} ({t.num_leechs})",
                    # 'comment': t.comment,
                }
                for t in torrents
            ]
        )
printing.table(tbl)
print()

categories = []
for state, torrents in torrents_by_state.items():
    remaining = sum(t.amount_left for t in torrents)
    categories.append(
        {
            'state': state,
            'count': len(torrents),
            'size': strings.file_size(sum(t.total_size for t in torrents)),
            'remaining': strings.file_size(remaining) if remaining else None,
            'file_count': sum(len(t.files) for t in torrents) if args.verbose >= 1 else None,  # a bit slow
        }
    )
printing.table(iterables.list_dict_filter_bool(categories))
print()

transfer = qbt_client.transfer_info()
print(transfer.connection_status.upper())

dl_speed = strings.file_size(transfer.dl_info_speed)
dl_limit = f'[{strings.file_size(transfer.dl_rate_limit)}/s]' if transfer.dl_rate_limit > 0 else ''
dl_d = strings.file_size(transfer.dl_info_data)
print(f"DL {dl_speed}/s {dl_limit} ({dl_d})")

up_speed = strings.file_size(transfer.up_info_speed)
up_limit = f'[{strings.file_size(transfer.up_rate_limit)}/s]' if transfer.up_rate_limit > 0 else ''
up_d = strings.file_size(transfer.up_info_data)
print(f"UP {up_speed}/s {up_limit} ({up_d})")
