#!/usr/bin/python3
import argparse
import json
import sys
from argparse import ArgumentParser

import pandas as pd


def jsonl_to_csv(input_file, output_file):
    df = pd.DataFrame([json.loads(line) for line in input_file])
    df.to_csv(output_file, index=False)


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
