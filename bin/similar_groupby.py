#!/usr/bin/python3
import argparse
import difflib
import sys

from tabulate import tabulate

from library.utils import argparse_utils, processes, strings


def s(args, line):
    return strings.path_to_sentence(line.lower() if args.ignore_case else line)


def main():
    parser = argparse_utils.ArgumentParser(description='Relaxed group-by using difflib')
    parser.add_argument('--ignore-case', '-i', action='store_true', help='Ignore upper-case')
    parser.add_argument('--stable', action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument('--minimum-similarity', '-m', type=float, default=0.3)
    parser.add_argument('--maximum-similarity', '-M', type=float, default=1.0)

    parser.add_argument(
        "lines", nargs="*", default=argparse_utils.STDIN_DASH, action=argparse_utils.ArgparseArgsOrStdinGen
    )
    parser.add_argument('input_path', type=argparse.FileType('r'), nargs='?', default=sys.stdin)
    args = parser.parse_args()

    if not (0.0 <= args.minimum_similarity <= 1.0):
        raise ValueError("minimum-similarity must be between 0.0 and 1.0")
    if not (0.0 <= args.maximum_similarity <= 1.0):
        raise ValueError("maximum-similarity must be between 0.0 and 1.0")

    lines = args.input_path.readlines()
    if not lines:
        processes.no_media_found()

    groups = []
    for line in lines:
        found_group = False
        for group in groups:
            if args.stable:
                representative_line = group[0]  # first example
            else:
                representative_line = group[-1]  # most recent match

            matcher = difflib.SequenceMatcher(None, s(args, line), s(args, representative_line))
            if args.maximum_similarity >= matcher.ratio() >= args.minimum_similarity:
                group.append(line)
                found_group = True
                break

        if not found_group:
            groups.append([line])  # add a new group

    table_data = []
    for group in groups:
        count = len(group)
        first_example = group[0]
        table_data.append([count, first_example])
    table_data.sort(key=lambda x: x[0], reverse=True)
    headers = ["Count", "Example"]

    print(tabulate(table_data, headers=headers, tablefmt="grid"))


if __name__ == '__main__':
    main()
