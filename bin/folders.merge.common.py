#!/usr/bin/env python3
"""
Directory Merge Script
Scans source and destination directories for matching folder names (1:1 only),
displays statistics, and merges them after confirmation.
"""

import os
import shutil
import sys
from collections import defaultdict

from library.utils import devices, strings
from tabulate import tabulate


def get_all_folders(root_path):
    """Get all non-empty folders in a directory tree."""
    folders = []
    for dirpath, dirnames, filenames in os.walk(root_path):
        # Skip empty folders (no files in this folder or any subdirectories)
        if filenames or any(os.listdir(os.path.join(dirpath, d)) for d in dirnames):
            rel_path = os.path.relpath(dirpath, root_path)
            if rel_path != '.':
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


def merge_folders(src_path, dest_path, src_folder, dest_folder):
    src_full = os.path.join(src_path, src_folder)
    dest_full = os.path.join(dest_path, dest_folder)

    merged_count = 0
    for dirpath, _, filenames in os.walk(src_full):
        # Calculate relative path from src_folder
        rel_path = os.path.relpath(dirpath, src_full)

        # Create corresponding directory in destination
        if rel_path != '.':
            dest_dir = os.path.join(dest_full, rel_path)
        else:
            dest_dir = dest_full

        os.makedirs(dest_dir, exist_ok=True)

        for filename in filenames:
            src_file = os.path.join(dirpath, filename)
            dest_file = os.path.join(dest_dir, filename)

            try:
                shutil.move(src_file, dest_file)
                merged_count += 1
            except Exception as e:
                print(f"  Error copying {src_file}: {e}")

    return merged_count


def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <source_path> <destination_path>")
        sys.exit(1)

    src_path = sys.argv[1]
    dest_path = sys.argv[2]
    if not os.path.isdir(src_path):
        print(f"Error: Source path '{src_path}' is not a valid directory")
        sys.exit(1)
    if not os.path.isdir(dest_path):
        print(f"Error: Destination path '{dest_path}' is not a valid directory")
        sys.exit(1)

    matches = find_matching_folders(src_path, dest_path)
    if not matches:
        print("No 1:1 matching folders found.")
        sys.exit(0)

    matches.sort(key=lambda x: x[0])

    total_dest_files = 0
    total_dest_size = 0
    total_move_files = 0
    total_move_size = 0
    table_data = []
    for src_folder, dest_folder in matches:
        src_count, src_size = get_folder_stats(src_path, src_folder)
        dest_count, dest_size = get_folder_stats(dest_path, dest_folder)

        total_dest_files += dest_count
        total_dest_size += dest_size
        total_move_files += src_count
        total_move_size += src_size

        after_count = dest_count + src_count
        after_size = dest_size + src_size

        table_data.append(
            [
                src_folder,
                dest_count,
                strings.file_size(dest_size),
                src_count,
                strings.file_size(src_size),
                after_count,
                strings.file_size(after_size),
            ]
        )

    total_after_files = total_dest_files + total_move_files
    total_after_size = total_dest_size + total_move_size
    table_data.append(
        [
            "TOTAL",
            total_dest_files,
            strings.file_size(total_dest_size),
            total_move_files,
            strings.file_size(total_move_size),
            total_after_files,
            strings.file_size(total_after_size),
        ]
    )

    headers = ["Folder Path", "Dest: Files", "Dest: Size", "Move: Files", "Move: Size", "After: Files", "After: Size"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    print()

    if not devices.confirm("Proceed with merge?"):
        sys.exit(141)

    for src_folder, dest_folder in matches:
        merge_folders(src_path, dest_path, src_folder, dest_folder)


if __name__ == "__main__":
    main()
