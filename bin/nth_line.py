#!/usr/bin/env -S python -S

import argparse
import sys

def main(args):
    n = args.n
    from_line = args.from_line

    for idx, line in enumerate(sys.stdin, start=1):
        if idx < from_line:
            continue
        if (idx - from_line) % n == 0:
            print(line, end='')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Take every <n>th line from stdin, optionally starting from <from>."
    )
    parser.add_argument(
        "n",
        type=int,
        nargs="?",
        default=1,
        help="The interval for selecting lines (e.g., 2 for every second line). Defaults to 1."
    )
    parser.add_argument(
        "--from",
        dest="from_line",
        type=int,
        help="The starting line number. Defaults to 'n' if not specified."
    )

    args = parser.parse_args()

    if args.from_line is None:
        args.from_line = args.n

    main(args)
