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
torrents = [t for t in torrents if not t.state_enum.is_complete]
print(len(torrents), 'downloading')

df = pd.DataFrame(
    {
        "hash": [t.hash for t in torrents],
        "progress": [t.progress for t in torrents],
        "remaining": [t.amount_left for t in torrents],
        "num_complete": [t.num_complete for t in torrents],
        "num_incomplete": [t.num_incomplete for t in torrents],
        "num_leechs": [t.num_leechs for t in torrents],
        "tracker": [qbt_get_tracker(qbt_client, t) for t in torrents],
        "tracker_count": iterables.value_counts([qbt_get_tracker(qbt_client, t) for t in torrents]),
    }
)


ranked_df = rank_dataframe(
    df,
    column_weights={
        "remaining": {"weight": 15},
        "num_complete": {"weight": 5},
        "num_leechs": {"direction": "desc", "weight": 4},
        "num_incomplete": {"direction": "desc", "weight": 3},
        "tracker_count": {"weight": 2, "bin": 4},
        "progress": {"direction": "desc", "weight": 1},
    },
)

ranked = ranked_df.to_dict('records')
ranked = sorted(
    ranked,
    key=lambda d: (
        d["progress"] > 0,
        d["tracker"] in ["jptv.club", "avistaz.to"],
        d["progress"] > 0.03,
        d["progress"] > 0.1,
    ),
    reverse=True,
)

for d in ranked:
    qbt_client.torrents_bottom_priority(torrent_hashes=[d["hash"]])
