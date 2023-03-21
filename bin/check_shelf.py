#!/usr/bin/python

import argparse, shelve
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('database', help='The name of the shelve database file to check')
    args = parser.parse_args()

    db = shelve.open(str(Path(args.database).resolve()), 'r')
    for key, value in db.items():
        print(f'{key}: {value}')

    db.close()

if __name__ == '__main__':
    main()
