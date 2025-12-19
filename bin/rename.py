#!/usr/bin/python3
import argparse
import os
import re

from library.utils import arggroups, argparse_utils, consts, devices, shell_utils
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

    for source_path in args.paths:
        if not os.path.exists(source_path):
            log.warning("Does not exist %s (skipping)", source_path)
            continue

        dest_path = REGEX_SEARCH.sub(args.replace_pattern, source_path)

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
