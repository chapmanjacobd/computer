#!/usr/bin/env python3

import argparse
import shlex
import sys
import webbrowser

from library.utils.log_utils import log
from library.utils.processes import cmd


def process_args(args):
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue  # Skip empty lines

        split_line = line.split('␟')  # Unit Separator
        if not split_line:
            continue

        result = cmd(*args.command1, '--', *split_line)
        stdout_lines = result.stdout.strip().splitlines()

        if len(stdout_lines) == 0:
            log.info("No matches %s", line)
        elif len(stdout_lines) == 1:
            new_args = stdout_lines[0].split('␟')
            cmd(*args.command2, '--', *new_args)
        else:
            # print(line)

            browsing_success = webbrowser.open(line, new=2, autoraise=False)
            if browsing_success is False:
                log.info("Problem opening %s", line)


def main():
    parser = argparse.ArgumentParser(description="Execute commands based on stdin and stdout")
    parser.add_argument("command1", type=shlex.split, help="The first command to execute.")
    parser.add_argument("command2", type=shlex.split, help="The second command to execute if stdout is one line.")
    args = parser.parse_args()

    process_args(args)


if __name__ == "__main__":
    main()
