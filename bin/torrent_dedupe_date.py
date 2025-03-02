#!/usr/bin/python3

import os
import re
from collections import defaultdict
from pathlib import Path

from library.utils import arg_utils, arggroups, argparse_utils
from torrentool.api import Torrent

parser = argparse_utils.ArgumentParser()
parser.add_argument('-r', '--remove', action='store_true', help='Actually remove files')
arggroups.debug(parser)

arggroups.paths_or_stdin(parser)
args = parser.parse_args()
arggroups.args_post(args, parser)


def extract_date(filename):
    match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    if match:
        return match.group(1)
    return None


clusters = defaultdict(list)
for path in list(arg_utils.gen_paths(args, ['.torrent'])):
    path = Path(path)
    date = extract_date(path.stem)
    if date:
        clusters[date].append(path)

for date, files in clusters.items():
    print(date, len(files))
    if len(files) > 1:
        sizes = {}
        for file in files:
            try:
                torrent = Torrent.from_file(file)
                sizes[file] = sum(f.length for f in torrent.files)
            except Exception:
                print(file)
                raise

        sorted_files = sorted(files, key=lambda f: sizes[f], reverse=True)
        file_to_remove = sorted_files[0]
        if args.remove:
            try:
                os.remove(file_to_remove)
            except OSError as e:
                print(f"Error removing {file_to_remove}: {e}")
        else:
            print(sizes)
            print('would remove', file_to_remove)
