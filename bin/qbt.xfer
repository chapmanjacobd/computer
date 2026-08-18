#!/usr/bin/python3
from library.mediafiles import torrents_start
from library.utils import arggroups, argparse_utils, strings


def parse_args():
    parser = argparse_utils.ArgumentParser()
    arggroups.qBittorrent(parser)
    arggroups.debug(parser)

    args = parser.parse_args()
    arggroups.args_post(args, parser)
    return args


args = parse_args()

qbt_client = torrents_start.start_qBittorrent(args)

transfer = qbt_client.transfer_info()
print(transfer.connection_status.upper())

dl_speed = strings.file_size(transfer.dl_info_speed)
dl_limit = f"[{strings.file_size(transfer.dl_rate_limit)}/s]" if transfer.dl_rate_limit > 0 else ""
dl_d = strings.file_size(transfer.dl_info_data)
print(f"DL {dl_speed}/s {dl_limit} ({dl_d})")

up_speed = strings.file_size(transfer.up_info_speed)
up_limit = f"[{strings.file_size(transfer.up_rate_limit)}/s]" if transfer.up_rate_limit > 0 else ""
up_d = strings.file_size(transfer.up_info_data)
print(f"UP {up_speed}/s {up_limit} ({up_d})")
