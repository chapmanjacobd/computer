#!/usr/bin/python3
import argparse
import os
import sys
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


def clean_directory(args):
    if not os.path.isdir(args.directory):
        print(f"Error: Directory '{args.directory}' not found.")
        sys.exit(1)

    for root, _dirs, files in os.walk(args.directory):
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


def main():
    parser = argparse.ArgumentParser(
        description="Remove empty folders and small files, with confirmation for non-whitelisted files."
    )
    parser.add_argument("directory", type=str, help="The target directory to clean.")
    parser.add_argument(
        "--max-size-mb",
        type=float,
        default=1.0,
        help="Maximum size in MB for files to be considered 'small' (default: 1.0MB).",
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

    clean_directory(args)


if __name__ == "__main__":
    main()
