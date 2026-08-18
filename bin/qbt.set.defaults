#!/usr/bin/python3
from library import usage
from library.mediafiles.torrents_start import start_qBittorrent
from library.utils import arggroups, argparse_utils, nums


def parse_args():
    parser = argparse_utils.ArgumentParser(usage=usage.torrents_start)
    arggroups.qBittorrent(parser)
    parser.add_argument(
        "--download-limit", "--dl-limit", required=True, type=nums.human_to_bytes, help="Global download limit"
    )
    parser.add_argument(
        "--upload-limit", "--up-limit", "--ul-limit", type=nums.human_to_bytes, help="Global upload limit"
    )
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
        "recheck_completed_torrents": False,
        "add_stopped_enabled": False,
        "connection_speed": 50,
        "dl_limit": args.download_limit,
        "up_limit": args.upload_limit or args.download_limit,
        "alt_dl_limit": args.download_limit // 3,
        "alt_up_limit": (args.upload_limit or args.download_limit) // 3,
        "max_active_downloads": 1,
        "max_active_uploads": max_active_uploads,
        "max_active_torrents": max_active_uploads + 1,
        "max_active_checking_torrents": 4,
        "slow_torrent_inactive_timer": 120,
        "refresh_interval": 3000,
        "save_resume_data_interval": 120,
        "memory_working_set_limit": 5000,
        "disk_io_type": 2,  # POSIX-compliant
        "schedule_from_hour": 9,
        "schedule_to_hour": 22,
        "scheduler_enabled": False,
        # divide by 50 but also bps -> kbps
        "slow_torrent_dl_rate_threshold": (args.download_limit) // 50_000,  # type: ignore
        "slow_torrent_ul_rate_threshold": (args.upload_limit or args.download_limit) // 50_000,  # type: ignore
    }
)
