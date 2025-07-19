#!/usr/bin/python3
import argparse
import os
from collections import Counter
from pathlib import Path
import charset_normalizer

from library.utils import arggroups, consts, devices, path_utils, printing, processes, strings


def print_info(p):
    print(os.path.basename(p))
    print(strings.file_size(os.path.getsize(p)), processes.cmd("file", "-bi", p).stdout, end='')

    try:
        b = Path(p).read_bytes()
    except IOError as e:
        print(f"Error reading file '{p}': {e}")
        return

    detection_result = charset_normalizer.from_bytes(b).best()
    if detection_result:
        try:
            print(str(detection_result))
        except Exception as e:
            print(b[0:250].hex(' ', 4))
    else:
        print(b[0:250].hex(' ', 4))

    print()


def clean_directory(args, directory):
    small_files = set()

    for root, _dirs, files in os.walk(directory):
        for file in files:
            p = os.path.join(root, file)
            file_size_mb = os.path.getsize(p) / (1024 * 1024)

            if file_size_mb > args.max_size_mb:
                print('Skipping large file', p)
            elif (
                os.path.splitext(file)[1].lower().lstrip('.')
                in consts.SUBTITLE_EXTENSIONS | consts.CALIBRE_EXTENSIONS | consts.ARCHIVE_EXTENSIONS
            ):
                print('Skipping subtitle/eBook/archive file', p)
            else:
                small_files.add(p)

    if not small_files:
        return

    extensions = Counter([os.path.splitext(file)[1].lower() for file in small_files])
    printing.table([extensions])
    if len(small_files) < 10 or devices.confirm('Delete?'):
        for p in small_files:
            print_info(p)
            os.remove(p)


def get_dir_size(path):
    total_size = 0
    for dirpath, _dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


def main():
    parser = argparse.ArgumentParser()
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

    arggroups.debug(parser)
    args = parser.parse_args()

    for directory in args.directories:
        if not os.path.isdir(directory):
            print(f"Error: Directory '{directory}' not found.")
            continue

        dir_size = get_dir_size(directory)
        dir_size_mb = dir_size / (1024 * 1024)
        if args.max_dir_size_mb and dir_size_mb > args.max_dir_size_mb:
            print(
                f"Skipping directory '{directory}' as its size ({strings.file_size(dir_size)}) "
                f"exceeds the maximum allowed ({args.max_dir_size_mb:.2f} MB)."
            )
            continue

        clean_directory(args, directory)
        path_utils.bfs_removedirs(directory)


if __name__ == "__main__":
    main()
