#!/usr/bin/env python3
"""
Directory Merge Script
Scans source and destination directories for matching folder names (1:1 only),
displays statistics, and merges them after confirmation.
"""

import os
import shutil
import sys
import argparse
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


def merge_folders(src_root, src_rel, dest_root, dest_rel):
    src_full = os.path.join(src_root, src_rel)
    dest_full = os.path.join(dest_root, dest_rel)
    merged_count = 0
    for dirpath, _, filenames in os.walk(src_full):
        # Calculate relative path from src_folder
        rel_path = os.path.relpath(dirpath, src_full)
        dest_dir = dest_full if rel_path == "." else os.path.join(dest_full, rel_path)
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
    totals = {"m_files": 0, "m_size": 0, "a_files": 0, "a_size": 0}
    table_data = []
    for s_rel, d_rel in matches:
        s_stats = {"root": args.src, "rel": s_rel, "count": 0, "size": 0}
        d_stats = {"root": args.dest, "rel": d_rel, "count": 0, "size": 0}
        s_stats["count"], s_stats["size"] = get_folder_stats(s_stats["root"], s_stats["rel"])
        d_stats["count"], d_stats["size"] = get_folder_stats(d_stats["root"], d_stats["rel"])

        swapped = args.smallest_move and s_stats["size"] > d_stats["size"]
        src, dest = (d_stats, s_stats) if swapped else (s_stats, d_stats)

        actions.append((src["root"], src["rel"], dest["root"], dest["rel"]))

        after_files = s_stats["count"] + d_stats["count"]
        after_size = s_stats["size"] + d_stats["size"]

        totals["m_files"] += src["count"]
        totals["m_size"] += src["size"]
        totals["a_files"] += after_files
        totals["a_size"] += after_size

        path_label = f"{s_rel} {'(dest)' if swapped else ''}"
        table_data.append(
            [
                path_label,
                src["count"],
                strings.file_size(src["size"]),
                after_files,
                strings.file_size(after_size),
            ]
        )

    table_data.append(
        [
            "TOTAL",
            totals["m_files"],
            strings.file_size(totals["m_size"]),
            totals["a_files"],
            strings.file_size(totals["a_size"]),
        ]
    )

    headers = [
        "Folder (Rel)",
        "Move: Files",
        "Move: Size",
        "Total: Files",
        "Total: Size",
    ]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

    if devices.confirm("\nProceed with merge?"):
        for action in actions:
            merge_folders(*action)


if __name__ == "__main__":
    main()
