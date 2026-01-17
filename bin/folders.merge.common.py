#!/usr/bin/env python3
"""
Duplicate Folder Merge Script
Scans one or more directories for duplicate folder names and proposes
merging them into the shallowest depth location.
"""

import os
import shutil
import sys
from collections import defaultdict

from library.utils import arggroups, argparse_utils, devices, nums, path_utils, strings
from tabulate import tabulate


def get_all_folders(root_paths, exclude_names):
    """Get all folders from root paths with their stats."""
    folders = defaultdict(list)  # basename -> list of (root, rel_path, depth)

    for root_path in root_paths:
        for dirpath, dirnames, filenames in os.walk(root_path):
            # Filter out excluded folder names
            dirnames[:] = [d for d in dirnames if d not in exclude_names]

            # Skip empty folders
            if not filenames and not dirnames:
                continue

            rel_path = os.path.relpath(dirpath, root_path)
            if rel_path == ".":
                continue

            basename = os.path.basename(dirpath)
            if basename.casefold() in exclude_names:
                continue

            if basename.isnumeric():
                continue

            depth = rel_path.count(os.sep)
            folders[basename].append((root_path, rel_path, depth))

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


def find_duplicate_folders(args):
    all_folders = get_all_folders(args.paths, args.exclude)
    duplicates = {name: locations for name, locations in all_folders.items() if len(locations) > 1}

    merge_groups = []
    for basename, locations in duplicates.items():
        # Collect stats for each location
        folder_data = []
        total_files = 0
        total_size = 0

        for root, rel_path, depth in locations:
            count, size = get_folder_stats(root, rel_path)

            # Apply individual folder constraints
            if args.min_count is not None and count < args.min_count:
                continue
            if args.max_count is not None and count > args.max_count:
                continue
            if args.min_size is not None and size < args.min_size:
                continue
            if args.max_size is not None and size > args.max_size:
                continue

            folder_data.append({'root': root, 'rel_path': rel_path, 'depth': depth, 'count': count, 'size': size})
            total_files += count
            total_size += size

        # Need at least 2 folders after filtering
        if len(folder_data) < 2:
            continue

        # Apply aggregate constraints
        if args.max_total_count is not None and total_files > args.max_total_count:
            continue
        if args.max_total_size is not None and total_size > args.max_total_size:
            continue

        # Sort by depth (shallowest first), then by path for consistency
        folder_data.sort(key=lambda x: (x['depth'], x['root'], x['rel_path']))

        # First folder (shallowest) is the destination
        dest = folder_data[0]
        sources = folder_data[1:]

        merge_groups.append(
            {
                'basename': basename,
                'dest': dest,
                'sources': sources,
                'total_files': total_files,
                'total_size': total_size,
            }
        )

    return merge_groups


def merge_folders(src, dest):
    """Merge src folder into dest folder."""
    merged_count = 0
    for dirpath, _, filenames in os.walk(src):
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
    parser = argparse_utils.ArgumentParser(
        description="Find and merge duplicate folder names into shallowest location."
    )
    parser.add_argument(
        "--exclude",
        "-E",
        action=argparse_utils.ArgparseList,
        default=[],
        help="Folder names to exclude (can be specified multiple times)",
    )
    parser.add_argument("--min-count", type=int, help="Minimum file count per folder")
    parser.add_argument("--max-count", type=int, help="Maximum file count per folder")
    parser.add_argument("--max-total-count", type=int, help="Maximum total file count across all duplicates")
    parser.add_argument("--min-size", type=nums.human_to_bytes, help="Minimum folder size (e.g., 10MB, 1GB)")
    parser.add_argument("--max-size", type=nums.human_to_bytes, help="Maximum folder size (e.g., 100MB, 5GB)")
    parser.add_argument(
        "--max-total-size", type=nums.human_to_bytes, help="Maximum total size across all duplicates (e.g., 1GB)"
    )
    arggroups.debug(parser)

    parser.add_argument("paths", nargs="+", help="One or more root directories to scan")
    args = parser.parse_args()

    # Validate paths
    for path in args.paths:
        if not os.path.isdir(path):
            print(f"Error: Invalid directory path: {path}")
            sys.exit(1)
    args.exclude = set(s.casefold() for s in args.exclude)

    merge_groups = find_duplicate_folders(args)
    if not merge_groups:
        print("No duplicate folders found matching criteria.")
        sys.exit(0)

    # Sort by basename for consistent output
    merge_groups.sort(key=lambda x: x['basename'])

    # Display results
    table_data = []
    total_move_files = 0
    total_move_size = 0

    for group in merge_groups:
        dest = group['dest']
        dest_path = os.path.join(dest['root'], dest['rel_path'])

        move_files = sum(src['count'] for src in group['sources'])
        move_size = sum(src['size'] for src in group['sources'])

        total_move_files += move_files
        total_move_size += move_size

        table_data.append(
            [
                group['basename'],
                len(group['sources']) + 1,  # Total duplicates
                move_files,
                strings.file_size(move_size),
                group['total_files'],
                strings.file_size(group['total_size']),
                # dest['depth'],
                # dest_path,
            ]
        )

    if table_data:
        print(f"Found {len(merge_groups)} duplicate folder name(s):")

        table_data.append(["TOTAL", "", total_move_files, strings.file_size(total_move_size), "", ""])
        print(
            tabulate(
                table_data,
                headers=[
                    "Folder Name",
                    "Dups",
                    "Move: Files",
                    "Move: Size",
                    "Total: Files",
                    "Total: Size",
                    # "Dest Depth",
                    # "Destination Path",
                ],
                tablefmt="grid",
            )
        )
        print()

        if args.simulate:
            print("Simulating merging:")
        elif not devices.confirm("Proceed with merge?"):
            return
        print()

        for group in merge_groups:
            dest_path = os.path.join(group['dest']['root'], group['dest']['rel_path'])
            print(f"Merging {group['basename']}")

            for src in group['sources']:
                src_path = os.path.join(src['root'], src['rel_path'])
                print(src_path)

                if not args.simulate:
                    merge_folders(src_path, dest_path)
                    path_utils.bfs_removedirs(src_path)

            print("-->", dest_path)
            print()

if __name__ == "__main__":
    main()
