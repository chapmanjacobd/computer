#!/usr/bin/python3
import argparse
import os
from collections import defaultdict
from library.utils.log_utils import log

def find_case_conflicts(root_dir):
    conflicts = defaultdict(list)
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Check directories
        lower_dirnames = defaultdict(list)
        for dname in dirnames:
            lower_dirnames[dname.casefold()].append(os.path.join(dirpath, dname))

        for lower_name, paths in lower_dirnames.items():
            if len(paths) > 1:
                conflicts[lower_name].extend(paths)

        # Check files
        # TODO: compare across all files (or after merging directories) to prevent future case conflicts
        lower_filenames = defaultdict(list)
        for fname in filenames:
            lower_filenames[fname.casefold()].append(os.path.join(dirpath, fname))

        for lower_name, paths in lower_filenames.items():
            if len(paths) > 1:
                conflicts[lower_name].extend(paths)
    return conflicts


def choose_preferred_path(paths):
    mixedcase_paths = [p for p in paths if not os.path.basename(p).islower() and not os.path.basename(p).isupper()]
    if mixedcase_paths:
        return mixedcase_paths[0]

    return paths[0]


def merge_conflicts(conflicts_map):
    if not conflicts_map:
        log.warning("No case conflicts found.")
        return

    for lower_name, paths in conflicts_map.items():
        log.warning(f"\nConflict detected for '{lower_name}':")
        for i, p in enumerate(paths):
            log.warning(f"  [{i+1}] {p}")

        preferred_path = choose_preferred_path(paths)
        if not os.path.exists(preferred_path):
            log.warning(f"  Warning: Preferred path '{preferred_path}' no longer exists. Skipping this conflict.")
            continue

        for current_path in paths:
            if current_path == preferred_path:
                continue  # Skip the chosen path
            if not os.path.exists(current_path):
                log.info(f"  '{current_path}' no longer exists, skipping.")
                continue

            print("lb mv", current_path, preferred_path)


def main():
    parser = argparse.ArgumentParser(
        description="Identify and merge case conflicts for files and folders in a filesystem."
    )
    parser.add_argument("directory", type=str, help="The root directory to scan for case conflicts.")
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()

    root_directory = args.directory

    if not os.path.isdir(root_directory):
        log.error(f"Error: '{root_directory}' is not a valid directory.")
        return

    conflicts = find_case_conflicts(root_directory)

    if not conflicts:
        log.warning("No case conflicts found in the specified directory.")
        return

    if args.run:
        merge_conflicts(conflicts)
    else:
        print("\n--- Identified Case Conflicts ---")
        for lower_name, paths in conflicts.items():
            print(f"Conflicts for '{lower_name}':")
            for p in paths:
                print(f"  - {p}")



if __name__ == "__main__":
    main()
