#!/usr/bin/python3
import argparse
import os
import random

from library.utils import argparse_utils


def fast_glob(args, path_dir):
    files = []
    try:
        with os.scandir(path_dir) as entries:
            for entry in entries:
                if args.ext and not entry.path.lower().endswith(args.ext):
                    continue

                if entry.is_file():
                    files.append(entry.path)
                    if len(files) == (args.max_files_per_dir * 10):
                        break
        return files
    except FileNotFoundError:
        return []


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-files", type=int, help="Maximum number of files")
    parser.add_argument("--max-folders", type=int, default=150, help="Maximum number of unique folders to process")
    parser.add_argument(
        "--max-files-per-dir", type=int, default=1, help="Maximum number of random files to choose per directory"
    )
    parser.add_argument(
        "--ext",
        "--exts",
        "--extensions",
        "-e",
        default=[],
        action=argparse_utils.ArgparseList,
        help="Include only specific file extensions",
    )

    parser.add_argument(
        "root_directory", default='.', type=os.path.realpath, help="The root directory to start searching from."
    )
    args = parser.parse_args()
    args.ext = tuple([s.lower() for s in args.ext])

    if not os.path.exists(args.root_directory):
        print(f"Error: Root directory '{args.root_directory}' does not exist.")
        raise SystemExit(1)

    num_files = 0
    unique_directories = set()
    for dirpath, _dirnames, _filenames in os.walk(args.root_directory):
        files_in_dir = fast_glob(args, dirpath)
        if files_in_dir:
            unique_directories.add(dirpath)
            if args.max_folders and len(unique_directories) > args.max_folders:
                break

            for file_path in random.sample(files_in_dir, min(len(files_in_dir), args.max_files_per_dir)):
                print(file_path)

                num_files += 1
                if args.max_files and num_files > args.max_files:
                    break


if __name__ == "__main__":
    main()
