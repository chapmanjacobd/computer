#!/usr/bin/python3
from datetime import datetime, timedelta

from library.mediafiles import torrents_start
from library.utils import arggroups, argparse_utils, devices, strings


def parse_args():
    parser = argparse_utils.ArgumentParser()
    arggroups.qBittorrent(parser)
    arggroups.debug(parser)

    args = parser.parse_args()
    arggroups.args_post(args, parser)
    return args


def is_dead_torrent(t):
    if t.state_enum.is_complete or t.state_enum.is_stopped or 'queued' in t.state:
        return False

    current_time = datetime.now()

    last_activity = datetime.fromtimestamp(t.last_activity)
    time_active = timedelta(seconds=t.time_active)

    no_peers = (
        t.progress == 0
        and (t.num_complete == 0 and t.num_incomplete == 0)
        and (t.last_activity is None or current_time - last_activity > timedelta(days=31))
    )
    low_progress = (t.progress < 0.1) and (time_active > timedelta(days=46))
    stuck = (t.progress >= 0.10) and (time_active > timedelta(days=61))

    return no_peers or low_progress or stuck


args = parse_args()

qbt_client = torrents_start.start_qBittorrent(args)
torrents = qbt_client.torrents_info()
torrents = [t for t in torrents if is_dead_torrent(t)]

print(len(torrents), 'found')
print()
for t in torrents:
    print(t.name)
    print(t.comment)
    print("State:", t.state)
    print("Added on:", strings.relative_datetime(t.added_on))
    print("Time active:", strings.duration(t.time_active))
    print("Last activity:", strings.relative_datetime(t.last_activity))
    print("Progress:", strings.percent(t.progress))
    print(f"Seeders: {t.num_seeds} ({t.num_complete}), Leechers: {t.num_leechs} ({t.num_incomplete})")
    print(t.content_path)

    if devices.confirm("Delete torrent and files?"):
        qbt_client.torrents_add_tags(['library-trumped'], torrent_hashes=[t.hash])
    print()
