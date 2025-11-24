#!/usr/bin/python3
import pandas as pd
from library.mediafiles import torrents_start
from library.playback import torrents_info
from library.text import regex_sort
from library.utils import arggroups, argparse_utils, iterables
from library.utils.pd_utils import rank_dataframe


def parse_args():
    parser = argparse_utils.ArgumentParser()
    arggroups.qBittorrent(parser)
    arggroups.text_filtering(parser)
    arggroups.regex_sort(parser)
    arggroups.debug(parser)

    args = parser.parse_args()
    arggroups.regex_sort_post(args)
    arggroups.args_post(args, parser)
    return args


args = parse_args()

qbt_client = torrents_start.start_qBittorrent(args)

torrents = qbt_client.torrents_info(tag="library")
print(len(torrents), 'total')
torrents = [t for t in torrents if not t.state_enum.is_complete]
print(len(torrents), 'downloading')

media = []
for t in torrents:
    media.append(
        {
            "name": t.name,
            "hash": t.hash,
            "progress": t.progress,
            "remaining": t.amount_left,
            "num_complete": t.num_complete,
            "num_leechs": t.num_leechs,
            "num_files": len(torrents_info.torrent_files(t)),
            "tracker": torrents_info.qbt_get_tracker(qbt_client, t),
            "private": t.private,
        }
    )

media = list(regex_sort.sort_dicts(args, media, search_columns=['name', 'tracker']))
media = iterables.list_dict_value_counts(media, "tracker")

df = pd.DataFrame(media)
df = rank_dataframe(
    df,
    column_weights={
        "num_complete": {"weight": 5},
        "num_leechs": {"weight": 4, "direction": "desc"},
        "remaining": {"bin": 4, "weight": 3},
        "num_files": {"weight": 2, "direction": "desc"},
        "tracker_count": {"bin": 6, "weight": 2},
        "progress": {"bin": 8, "weight": 1, "direction": "desc"},
    },
)
media = df.to_dict('records')

media = sorted(
    media,
    key=lambda d: (
        d["progress"] > 0,
        d["progress"] > 0.03,
        d["private"],
        d["remaining"] < 3719453952 // 16,
        d["remaining"] < 3719453952 // 4,
        d["remaining"] < 3719453952,
        d["remaining"] < 3719453952 * 4,
        d["remaining"] < 3719453952 * 16,
        d["tracker"] in ["privatehd.to", "avistaz.to"],
    ),
    reverse=True,
)

for d in media:
    qbt_client.torrents_bottom_priority(torrent_hashes=[d["hash"]])
