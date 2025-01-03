#!/usr/bin/python3
import pandas as pd
from library.mediafiles import torrents_start
from library.playback.torrents_info import qbt_get_tracker
from library.utils import arggroups, argparse_utils, iterables
from library.utils.pd_utils import rank_dataframe


def parse_args():
    parser = argparse_utils.ArgumentParser()
    arggroups.qBittorrent(parser)
    arggroups.debug(parser)

    args = parser.parse_args()
    arggroups.args_post(args, parser)
    return args


args = parse_args()

qbt_client = torrents_start.start_qBittorrent(args)


torrents = qbt_client.torrents_info(tag="library")
print(len(torrents), 'total')
torrents = [t for t in torrents if t.state_enum.is_downloading]
print(len(torrents), 'downloading')

df = pd.DataFrame(
    {
        "hash": [t.hash for t in torrents],
        "size": [t.size for t in torrents],
        "progress": [t.progress for t in torrents],
        "remaining": [t.amount_left for t in torrents],
        "tracker_count": iterables.value_counts([qbt_get_tracker(qbt_client, t) for t in torrents]),
    }
)


ranked_df = rank_dataframe(
    df,
    column_weights={
        "tracker_count": {"direction": "asc", "weight": 12},
        "remaining": {"direction": "asc", "weight": 7},
        "progress": {"direction": "desc", "weight": 6},
        "size": {"direction": "asc", "weight": 3},
    },
)

for t in ranked_df.itertuples():
    qbt_client.torrents_bottom_priority(torrent_hashes=[t.hash])  # type: ignore
