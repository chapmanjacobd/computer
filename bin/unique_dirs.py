#!/usr/bin/python3
import sys
import os
import random
import argparse
from typing import Dict, List

parser = argparse.ArgumentParser()
parser.add_argument('--files', nargs='?', type=int, const=1, help='Print N random files per directory instead of directories')
args = parser.parse_args()

files_per_dir: Dict[str, List[str]] = {}

for line in sys.stdin:
    line = line.strip()
    dir_name = os.path.dirname(line)

    if dir_name not in files_per_dir:
        files_per_dir[dir_name] = []
    files_per_dir[dir_name].append(line)

if args.files:
    for dir_name in files_per_dir:
        files = files_per_dir[dir_name]
        n = min(len(files), args.files)
        print('\n'.join(random.sample(files, n)))
else:
    for dir_name in files_per_dir:
        if not dir_name:
            continue
        print(dir_name + os.sep)
