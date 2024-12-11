from xklb.mediafiles import torrents_start
from xklb.utils import arggroups, argparse_utils

from torrentool.api import Torrent


def parse_args():
    parser = argparse_utils.ArgumentParser()
    arggroups.qBittorrent(parser)
    arggroups.debug(parser)

    args = parser.parse_args()
    arggroups.args_post(args, parser)
    return args


args = parse_args()

qbt_client = torrents_start.start_qBittorrent(args)
preferences = qbt_client.app_preferences()

raise
