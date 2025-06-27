#!/usr/bin/python3
import argparse
import os
import re
from pathlib import Path

import psutil
from library.utils import arggroups, argparse_utils, consts, devices, file_utils, path_utils
from library.utils.log_utils import log


def main():
    parser = argparse.ArgumentParser(
        description="Recursively rename files based on a regex pattern, "
        "creating parent directories if the new path implies them. "
        "Example: rename.py '^(.*)\\.txt$' 'new_folder/\\1.log' PATH ..."
    )
    parser.add_argument(
        "search_pattern",
        help="The regular expression to search for in filenames. "
        "Use raw strings (e.g., r'pattern') in your shell for complex regex to avoid issues with backslashes.",
    )
    parser.add_argument(
        "replace_pattern",
        help="The replacement string for the matched pattern. "
        "Can include backreferences (e.g., \\1, \\g<name>) for parts captured in the search_pattern. "
        "You can also specify new directory components here (e.g., 'new_subdir/\\1.ext').",
    )
    parser.add_argument('--re-parent', '--reparent')
    arggroups.clobber(parser)
    arggroups.debug(parser)

    parser.add_argument(
        'paths', nargs='*', default=argparse_utils.STDIN_DASH, action=argparse_utils.ArgparseArgsOrStdin
    )
    args = parser.parse_args()

    try:
        REGEX_SEARCH = re.compile(args.search_pattern)
    except re.error as e:
        log.error("ERROR: Invalid regular expression %s: %s", args.search_pattern, e)
        raise SystemExit(1)

    log.info('search: %s', REGEX_SEARCH)
    log.info('replacement: %s', args.replace_pattern)

    mountpoints = [
        '/mnt/d/',  # TODO: add better mergerfs support
    ] + sorted((partition.mountpoint for partition in psutil.disk_partitions()), key=len, reverse=True)

    for source_path in args.paths:
        if not os.path.exists(source_path):
            log.warning("Does not exist %s (skipping)", source_path)
            continue

        if args.re_parent:
            mount_path = None
            for mountpoint in mountpoints:
                if source_path.startswith(mountpoint):
                    mount_path = Path(mountpoint)
                    break
            if mount_path is None:
                mount_path = Path(path_utils.mountpoint(source_path))

            relative_src_parts = Path(source_path).parts[len(mount_path.parts) :]
            dest_path = str(Path(mount_path, args.re_parent.lstrip(os.sep), *relative_src_parts))

            if len(mount_path.parts) == 1:
                log.warning('Skipping root level re-parent to %s', dest_path)
                continue
        else:
            dest_path = REGEX_SEARCH.sub(args.replace_pattern, source_path)

        if args.verbose >= consts.LOG_INFO:
            print(source_path)
            print("-->", dest_path)

        if source_path == dest_path:
            log.info("No rename needed %s (skipping)", source_path)
            continue

        src, dest = devices.clobber(args, source_path, dest_path)
        file_utils.rename_move_file(src, dest, args.simulate)


if __name__ == "__main__":
    main()
