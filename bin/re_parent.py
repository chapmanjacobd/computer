#!/usr/bin/python3
import argparse
import os
from pathlib import Path

import psutil
from library.utils import arggroups, argparse_utils, consts, devices, shell_utils, path_utils
from library.utils.log_utils import log


def main():
    parser = argparse.ArgumentParser()
    arggroups.clobber(parser)
    arggroups.debug(parser)

    parser.add_argument('re_parent')
    parser.add_argument(
        'paths', nargs='*', default=argparse_utils.STDIN_DASH, action=argparse_utils.ArgparseArgsOrStdin
    )
    args = parser.parse_args()

    mountpoints = [
        '/mnt/d/',  # TODO: add better mergerfs support
    ] + sorted((partition.mountpoint for partition in psutil.disk_partitions()), key=len, reverse=True)

    for source_path in args.paths:
        if not os.path.exists(source_path):
            log.warning("Does not exist %s (skipping)", source_path)
            continue

        mount_path = None
        for mountpoint in mountpoints:
            if source_path.startswith(mountpoint):
                mount_path = Path(mountpoint)
                break
        if mount_path is None:
            mount_path = Path(path_utils.mountpoint(source_path))

        if str(mount_path) in ("/", "/home", "/var/home"):
            mountpoint = Path().home()

        relative_src_parts = Path(source_path).parts[len(mount_path.parts) :]
        dest_path = str(Path(mount_path, args.re_parent.lstrip(os.sep), *relative_src_parts))

        if len(mount_path.parts) == 1:
            log.warning('Skipping root level re-parent to %s', dest_path)
            continue

        if args.verbose >= consts.LOG_INFO:
            print(source_path)
            print("-->", dest_path)

        if source_path == dest_path:
            log.info("No rename needed %s (skipping)", source_path)
            continue

        try:
            src, dest = devices.clobber(args, source_path, dest_path)
            shell_utils.rename_move_file(src, dest, args.simulate)
        except PermissionError:
            log.info("Permission Error %s (skipping)", source_path)
            continue


if __name__ == "__main__":
    main()
