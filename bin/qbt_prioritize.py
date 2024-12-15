#!/usr/bin/python3
import pandas as pd
from library.mediafiles import torrents_start
from library.utils import arggroups, argparse_utils, printing, strings, objects


def parse_args():
    parser = argparse_utils.ArgumentParser()
    arggroups.qBittorrent(parser)
    arggroups.debug(parser)

    args = parser.parse_args()
    arggroups.args_post(args, parser)
    return args


def rank_dataframe(df, column_weights):
    ranks = df[column_weights.keys()].apply(
        lambda x: x.rank(
            method="min",
            na_option="bottom",
            ascending=column_weights.get(x.name, {}).get("direction") == "asc",
        )
        * column_weights.get(x.name, {}).get("weight", 1),
    )

    unranked_columns = set(df.select_dtypes(include=["number"]).columns) - set(ranks.columns)
    if unranked_columns:
        print(
            "Unranked columns:\n"
            + "\n".join([f"""    "{s}": {{ 'direction': 'desc' }}, """ for s in unranked_columns]),
        )

    scaled_ranks = (ranks - 1) / (len(ranks.columns) - 1)
    scaled_df = df.iloc[scaled_ranks.sum(axis=1).sort_values().index]
    return scaled_df.reset_index(drop=True)


args = parse_args()

qbt_client = torrents_start.start_qBittorrent(args)


torrents = qbt_client.torrents_info(status_filter="all")
torrents = [t for t in torrents if t.state_enum in ["stoppedDL", "metaDL", "stalledDL", "downloading"]]

df = pd.DataFrame(
    {
        "hash": [t.hash for t in torrents],
        "size": [t.size for t in torrents],
        "progress": [t.progress for t in torrents],
        "remaining": [t.amount_left for t in torrents],
    }
)


ranked_df = rank_dataframe(
    df,
    column_weights={
        "remaining": {"direction": "asc", "weight": 7},
        "progress": {"direction": "desc", "weight": 6},
        "size": {"direction": "asc", "weight": 3},
    },
)

for t in ranked_df.itertuples():
    qbt_client.torrents_bottom_priority(torrent_hashes=[t.hash])
