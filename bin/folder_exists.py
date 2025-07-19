#!/usr/bin/python3
import argparse
import os
import sys


def process_folders(args):
    for line in sys.stdin:
        folder_path = line.strip()
        if not folder_path:  # Skip empty lines
            continue

        if os.path.isdir(folder_path):
            try:
                has_content = any(o.is_file() for o in os.scandir(folder_path))
                if has_content:
                    print(folder_path)
                    continue
            except OSError as e:
                if args.verbose:
                    print(f"Warning: Could not scan directory '{folder_path}': {e}", file=sys.stderr)

        print(folder_path, file=sys.stderr)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true", help="Print messages for skipped directories to stderr.")
    args = parser.parse_args()

    process_folders(args)


if __name__ == "__main__":
    main()
