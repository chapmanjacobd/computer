#!/usr/bin/python3

import os
import re
from collections import defaultdict
from pathlib import Path

from library.utils import shell_utils, arggroups, argparse_utils, strings
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

paths = list(shell_utils.gen_paths(args, ['.torrent']))

clusters = defaultdict(list)
for path in paths:
    path = Path(path)
    date = extract_date(path.stem)
    if date:
        clusters[date].append(path)

originals = 0
for date, files in clusters.items():
    if len(files) > 1:
        print(len(files), date, sep='\t')

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
            for path, size in sizes.items():
                print('\t', strings.file_size(size), path)
            print('\t', 'would remove', file_to_remove)
        originals+=1
print()
print('Files:', len(paths), 'Originals:', originals, 'Unique:', len(clusters) - originals)
