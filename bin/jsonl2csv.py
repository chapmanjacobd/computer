#!/usr/bin/python3
import argparse
import csv
import json
import sys
from argparse import ArgumentParser
import pandas as pd
from xklb.utils import iterables


def jsonl_to_csv(input_file, output_file):
    json_data = [json.loads(line) for line in input_file]

    keys = list(iterables.ordered_set(l for d in json_data for l in d.keys()))

    writer = csv.DictWriter(output_file, fieldnames=keys)
    writer.writeheader()
    writer.writerows(json_data)


def main():
    parser = ArgumentParser(description='Convert JSON Lines to CSV.')
    parser.add_argument(
        'output_file',
        nargs='?',
        type=argparse.FileType('w'),
        default=sys.stdout,
        help='Output CSV file (default: stdout)',
    )
    args = parser.parse_args()

    jsonl_to_csv(sys.stdin, args.output_file)

    if args.output_file is not sys.stdout:
        args.output_file.close()


if __name__ == '__main__':
    main()
