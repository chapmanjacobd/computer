#!/usr/bin/python3
import argparse
import os
from pathlib import Path

from library.utils import processes, strings


def print_info(p):
    print(os.path.basename(p))
    print(strings.file_size(os.path.getsize(p)), processes.cmd("file", "-bi", p).stdout, end='')

    try:
        b = Path(p).read_bytes()

        try:
            decoded_text = b.decode('utf-8')
            print(decoded_text)
        except UnicodeDecodeError:
            print(b[0:250].hex(' ', 4))
    except IOError as e:
        print(f"Error reading file '{p}': {e}")

    print()


def clean_directory(args, directory):
    for root, _dirs, files in os.walk(directory):
        for file in files:
            p = os.path.join(root, file)
            file_size_mb = os.path.getsize(p) / (1024 * 1024)
            file_extension = os.path.splitext(file)[1].lower()

            if file_size_mb < args.max_size_mb:
                print_info(p)

                if file_extension in args.small_file_extensions:
                    os.remove(p)
                else:
                    response = input(f"Confirm erasure of '{p}'? (y/n): ").lower()
                    if response == 'y':
                        os.remove(p)
                    else:
                        print(f"Skipping: {p}")


def get_dir_size(path):
    total_size = 0
    for dirpath, _dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


def main():
    parser = argparse.ArgumentParser(
        description="Remove empty folders and small files, with confirmation for non-whitelisted files."
    )
    parser.add_argument("directories", metavar="DIRECTORY", type=str, nargs='+', help="The target directory to clean.")
    parser.add_argument(
        "--max-size-mb",
        type=float,
        default=1.0,
        help="Maximum size in MB for files to be considered 'small' (default: 1.0MB).",
    )
    parser.add_argument(
        "--max-dir-size-mb",
        type=float,
        default=5.0,
        help="Maximum size in MB for a directory to be processed. Directories larger than this will be skipped.",
    )
    parser.add_argument(
        "--small-file-extensions",
        nargs='*',
        default=['.ds_store', '.sfv', '.nfo', '.srr'],
        help="List of file extensions (e.g., .ds_store) to be removed if under --max-size-mb (case-insensitive).",
        metavar="EXT",
    )

    args = parser.parse_args()

    args.small_file_extensions = [ext.lower() for ext in args.small_file_extensions]

    for directory in args.directories:
        if not os.path.isdir(directory):
            print(f"Error: Directory '{directory}' not found.")
            continue

        dir_size_mb = get_dir_size(directory) / (1024 * 1024)
        if args.max_dir_size_mb and dir_size_mb > args.max_dir_size_mb:
            print(
                f"Skipping directory '{directory}' as its size ({dir_size_mb:.2f} MB) "
                f"exceeds the maximum allowed ({args.max_dir_size_mb:.2f} MB)."
            )
            continue

        clean_directory(args, directory)


if __name__ == "__main__":
    main()
