#!/usr/bin/python3

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from library.createdb import torrents_add
from library.utils import arggroups, argparse_utils, devices, file_utils, nums, printing, strings

parser = argparse_utils.ArgumentParser()
arggroups.capability_delete(parser)
parser.add_argument('paths', nargs='+', help='Path(s) to torrent files')
args = parser.parse_args()

torrent_files = [
    file for torrent_folder in args.paths for file in Path(torrent_folder).rglob('*.torrent') if not file.is_dir()
]
with ThreadPoolExecutor() as executor:
    metadata_results = executor.map(torrents_add.extract_metadata, torrent_files)
torrents = list(zip(torrent_files, metadata_results))


def get_detail(d):
    return {k: v for k, v in d.items() if k in ["author", "tracker", "comment", "title", "file_count", "path"]} | {
        "size": strings.file_size(d["size"]),
        "time_uploaded": strings.relative_datetime(d["time_uploaded"]),
    }


def comparison_table(d1, d2):
    printing.table([get_detail(d1), get_detail(d2)])


min_size = nums.human_to_bytes("2Mi")
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
        elif len(torrent1_files) > 1 and len(torrent1_files) == len(torrent2_files):
            sizes1 = sorted([f['size'] for f in torrent1_files])
            sizes2 = sorted([f['size'] for f in torrent2_files])
            if sizes1 == sizes2:
                is_dupe = True

        elif (len(torrent1_files) > 1 and len(torrent2_files) > 2) or (
            len(torrent1_files) > 2 and len(torrent2_files) > 1
        ):
            lengths_set1 = set(f1['size'] for f1 in torrent1_files if f1['size'] > min_size)
            lengths_set2 = set(f2['size'] for f2 in torrent2_files if f2['size'] > min_size)
            if not lengths_set1 or not lengths_set2:
                continue

            if lengths_set1.issubset(lengths_set2) or lengths_set1.issuperset(lengths_set2):
                is_dupe = True

            overlap_lengths = lengths_set1.intersection(lengths_set2)
            match_count = len(overlap_lengths)

            similarity = match_count / len(torrent1_files)
            if similarity > 0.3:
                print()
                print(strings.percent(similarity), "similar:")
                comparison_table(torrent1, torrent2)
                print()

        if is_dupe:
            torrent1["time_uploaded"] = torrent1["time_uploaded"] or torrent1["time_modified"] or torrent1["time_created"] or 0
            torrent2["time_uploaded"] = torrent2["time_uploaded"] or torrent2["time_modified"] or torrent2["time_created"] or 0

            key = str(torrent_path1)
            if key not in duplicates:
                duplicates[key] = []
            duplicates[key].append(torrent1)
            duplicates[key].append(torrent2)

print()
print(f"Exact duplicate groups ({len(duplicates)}):")
for group in sorted(duplicates, key=len, reverse=True):
    group = sorted(duplicates[group], key=lambda d: d["time_uploaded"])
    comparison_table(*group)
    print()

    torrent1_files = group[0]['files']
    torrent2_files = group[1]['files']
    if len(torrent1_files) != len(torrent2_files):
        lengths_set1 = set(f1['size'] for f1 in torrent1_files)
        lengths_set2 = set(f2['size'] for f2 in torrent2_files)

        if lengths_set1.issubset(lengths_set2):
            print("Delete left (Older, fewer files)")
            torrent_to_delete = group[0]
        elif lengths_set1.issuperset(lengths_set2):
            print("Delete right (Newer, fewer files)")
            torrent_to_delete = group[1]
        else:
            print("Delete left (Older, file lists differ)")
            torrent_to_delete = group[0]
    else:
        print("Delete left (Older, same file count)")
        torrent_to_delete = group[0]

    if devices.confirm("Delete?"):
        file_utils.trash(args, torrent_to_delete["path"])
