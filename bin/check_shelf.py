#!/usr/bin/python

import shelve
from pathlib import Path

from xklb.utils import argparse_utils


def main():
    parser = argparse_utils.ArgumentParser()
    parser.add_argument('database', help='The name of the shelve database file to check')
    args = parser.parse_args()

    db = shelve.open(str(Path(args.database).resolve()), 'r')
    for key, value in db.items():
        print(f'{key}: {value}')

    db.close()


if __name__ == '__main__':
    main()
