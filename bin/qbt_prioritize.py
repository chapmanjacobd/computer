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


SIZE_WEIGHT = 0.30
PROGRESS_WEIGHT = 0.70

args = parse_args()

qbt_client = torrents_start.start_qBittorrent(args)


torrents = qbt_client.torrents_info(status_filter="all")
torrents = [t for t in torrents if t.state_enum in ["stoppedDL", "metaDL", "stalledDL", "downloading"]]

torrents.sort(key=lambda t: (SIZE_WEIGHT * t.size) + (PROGRESS_WEIGHT * t.progress * 100))

for t in torrents:
    qbt_client.torrents_bottom_priority(torrent_hashes=[t.hash])
