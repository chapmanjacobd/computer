#!/usr/bin/python3

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from library.createdb import torrents_add
from library.utils import argparse_utils, strings

parser = argparse_utils.ArgumentParser()
parser.add_argument('paths', nargs='+', help='Path(s) to torrent files')
args = parser.parse_args()

torrent_files = [file for torrent_folder in args.paths for file in Path(torrent_folder).glob('*.torrent')]
with ThreadPoolExecutor() as executor:
    metadata_results = executor.map(torrents_add.extract_metadata, torrent_files)
torrents = list(zip(torrent_files, metadata_results))


def print_detail(d):
    print(d.get("author"), d.get("tracker"), d.get("comment"))
    print(d["title"], d["file_count"], "files", strings.relative_datetime(d["time_uploaded"] or d["time_modified"]))
    print("Example:", strings.file_size(d["files"][0]["size"]), d["files"][0]["path"])
    print(d["path"])


len_torrents = len(torrents)
duplicates = {}
for i, (torrent_path1, torrent1) in enumerate(torrents):
    # print_overwrite('Checking', i, 'of', len_torrents, f"({strings.percent(i/len_torrents)})")

    for torrent_path2, torrent2 in torrents[i + 1 :]:

        is_dupe = False
        torrent1_files = torrent1['files']
        torrent2_files = torrent2['files']
        if torrent1_files == torrent2_files:
            is_dupe = True
        elif len(torrent1_files) > 3 and len(torrent1_files) == len(torrent2_files):
            sizes1 = [f['size'] for f in torrent1_files]
            sizes2 = [f['size'] for f in torrent2_files]
            if sizes1 == sizes2:
                is_dupe = True

        elif len(torrent1_files) > 10 and len(torrent2_files) > 10:
            lengths_set1 = set(f1['size'] for f1 in torrent1_files)
            lengths_set2 = set(f2['size'] for f2 in torrent2_files)
            overlap_lengths = lengths_set1.intersection(lengths_set2)
            match_count = len(overlap_lengths)

            similarity = match_count / len(torrent1_files)
            if similarity > 0.3:
                print()
                print(strings.percent(similarity), "similar:")
                print_detail(torrent1)
                print_detail(torrent2)
                print()

        if is_dupe:
            key = str(torrent_path1)
            if key not in duplicates:
                duplicates[key] = []
            duplicates[key].append(torrent1)
            duplicates[key].append(torrent2)

print()
print(f"Exact duplicate groups ({len(duplicates)}):")
for group in sorted(duplicates, key=len, reverse=True):
    for d in sorted(duplicates[group], key=lambda d: d["time_uploaded"]):
        print_detail(d)
    print()
