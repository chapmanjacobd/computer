#!/usr/bin/python3
from library import usage
from library.mediafiles.torrents_start import start_qBittorrent
from library.utils import arggroups, argparse_utils, nums


def parse_args():
    parser = argparse_utils.ArgumentParser(usage=usage.torrents_start)
    arggroups.qBittorrent(parser)
    parser.add_argument(
        "--dl-limit",
        "--download-limit",
        required=True,
        type=nums.human_to_bytes,
        help="Download limit. If set then a few additional global preferences will also be changed",
    )
    parser.add_argument("--up-limit", "--ul-limit", "--upload-limit", type=nums.human_to_bytes, help="Upload limit")
    arggroups.debug(parser)

    args = parser.parse_args()
    arggroups.args_post(args, parser)
    return args


args = parse_args()

qbt_client = start_qBittorrent(args)

current_count = qbt_client.torrents_count()
max_active_uploads = current_count + 10_000

qbt_client.app_set_preferences(
    {
        "preallocate_all": True,
        "recheck_completed_torrents": True,
        "add_stopped_enabled": False,
        "dl_limit": args.dl_limit,
        "up_limit": args.up_limit or args.dl_limit,
        "max_active_downloads": 1,
        "max_active_uploads": max_active_uploads,
        "max_active_torrents": max_active_uploads + 1,
        "max_active_checking_torrents": 3,
        "slow_torrent_inactive_timer": 80,
        # divide by 10 but also some bps -> kbps BS
        "slow_torrent_dl_rate_threshold": (args.dl_limit) // 10_000,  # type: ignore
        "slow_torrent_ul_rate_threshold": (args.up_limit or args.dl_limit) // 10_000,  # type: ignore
    }
)
