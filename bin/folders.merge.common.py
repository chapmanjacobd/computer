#!/usr/bin/env python3
"""
Directory Merge Script
Scans source and destination directories for matching folder names (1:1 only),
displays statistics, and merges them after confirmation.
"""

import argparse
import os
import shutil
import sys
from collections import defaultdict

from library.utils import devices, strings
from tabulate import tabulate


def get_all_folders(root_path):
    folders = []
    for dirpath, dirnames, filenames in os.walk(root_path):
        # Skip empty folders (no files in this folder or any subdirectories)
        if filenames or any(os.listdir(os.path.join(dirpath, d)) for d in dirnames):
            rel_path = os.path.relpath(dirpath, root_path)
            if rel_path != ".":
                folders.append(rel_path)
    return folders


def get_folder_stats(root_path, rel_folder):
    """Get file count and total size for a folder."""
    folder_path = os.path.join(root_path, rel_folder)
    count = 0
    total_size = 0

    for dirpath, _, filenames in os.walk(folder_path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                total_size += os.path.getsize(filepath)
                count += 1
            except OSError:
                pass

    return count, total_size


def find_matching_folders(src_path, dest_path):
    """Find 1:1 matching folder names between src and dest."""
    src_folders = get_all_folders(src_path)
    dest_folders = get_all_folders(dest_path)

    # Get folder basenames and track duplicates
    src_basenames = defaultdict(list)
    dest_basenames = defaultdict(list)

    for folder in src_folders:
        basename = os.path.basename(folder)
        src_basenames[basename].append(folder)

    for folder in dest_folders:
        basename = os.path.basename(folder)
        dest_basenames[basename].append(folder)

    # Find 1:1 matches (no duplicates in either src or dest)
    matches = []
    for basename in src_basenames:
        if basename in dest_basenames and len(src_basenames[basename]) == 1 and len(dest_basenames[basename]) == 1:
            src_folder = src_basenames[basename][0]
            dest_folder = dest_basenames[basename][0]
            matches.append((src_folder, dest_folder))

    return matches


def merge_folders(src, dest):
    merged_count = 0
    for dirpath, _, filenames in os.walk(src):
        # Calculate relative path from src_folder
        rel_path = os.path.relpath(dirpath, src)
        dest_dir = dest if rel_path == "." else os.path.join(dest, rel_path)
        os.makedirs(dest_dir, exist_ok=True)

        for filename in filenames:
            src_file = os.path.join(dirpath, filename)
            dest_file = os.path.join(dest_dir, filename)

            try:
                shutil.move(src_file, dest_file)
                merged_count += 1
            except Exception as e:
                print(f"  Error moving {src_file}: {e}")

    return merged_count


def main():
    parser = argparse.ArgumentParser(description="Merge matching directories.")
    parser.add_argument("src", help="Source root path")
    parser.add_argument("dest", help="Destination root path")
    parser.add_argument(
        "--smallest-move",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Swap src/dest if dest is larger",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.src) or not os.path.isdir(args.dest):
        print("Error: Invalid directory paths.")
        sys.exit(1)

    matches = find_matching_folders(args.src, args.dest)
    if not matches:
        print("No 1:1 matching folders found.")
        sys.exit(0)

    matches.sort(key=lambda x: x[0])

    actions = []
    aggs = {
        "to_dest": {"f": 0, "s": 0, "count_all": 0, "size_all": 0},
        "to_src": {"f": 0, "s": 0, "count_all": 0, "size_all": 0},
    }
    table_data = []
    for s_rel, d_rel in matches:
        s_count, s_size = get_folder_stats(args.src, s_rel)
        d_count, d_size = get_folder_stats(args.dest, d_rel)
        if s_count == 0 or d_count == 0:
            continue

        src_info = {"r": args.src, "p": s_rel, "c": s_count, "s": s_size}
        dest_info = {"r": args.dest, "p": d_rel, "c": d_count, "s": d_size}

        swapped = args.smallest_move and s_size > d_size
        if swapped:
            src_info, dest_info = dest_info, src_info

        key = "to_src" if swapped else "to_dest"
        aggs[key]["f"] += src_info["c"]
        aggs[key]["s"] += src_info["s"]
        aggs[key]["count_all"] += s_count + d_count
        aggs[key]["size_all"] += s_size + d_size

        actions.append((os.path.join(src_info["r"], src_info["p"]), os.path.join(dest_info["r"], dest_info["p"])))
        table_data.append(
            [
                f"{s_rel} {'(dest)' if swapped else ''}",
                src_info["c"],
                strings.file_size(src_info["s"]),
                s_count + d_count,
                strings.file_size(s_size + d_size),
            ]
        )

    total_files = aggs["to_dest"]["f"] + aggs["to_src"]["f"]
    total_size = aggs["to_dest"]["s"] + aggs["to_src"]["s"]
    total_after_files = aggs["to_dest"]["count_all"] + aggs["to_src"]["count_all"]
    total_after_size = aggs["to_dest"]["size_all"] + aggs["to_src"]["size_all"]

    table_data.append(
        ["TOTAL", total_files, strings.file_size(total_size), total_after_files, strings.file_size(total_after_size)]
    )
    print(
        tabulate(
            table_data,
            headers=["Folder (Rel)", "Move: Files", "Move: Size", "Total: Files", "Total: Size"],
            tablefmt="grid",
        )
    )

    if aggs['to_dest']['f']:
        print(f"  Moved to Destination: {aggs['to_dest']['f']} files ({strings.file_size(aggs['to_dest']['s'])})")
    if aggs['to_src']['f']:
        print(f"  Moved to Source:       {aggs['to_src']['f']} files ({strings.file_size(aggs['to_src']['s'])})")

    if devices.confirm("\nProceed with merge?"):
        for action in actions:
            merge_folders(*action)


if __name__ == "__main__":
    main()
