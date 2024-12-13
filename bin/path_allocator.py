#!/usr/bin/python3
import concurrent.futures
from pathlib import Path

import humanize
from library.utils import argparse_utils, nums


def get_recursive_size(path):
    if path.is_file():
        return path.stat().st_size
    total_size = 0
    for item in path.rglob('*'):
        if item.is_file():
            total_size += item.stat().st_size
    return total_size


def main(directory, byte_limit):
    path = Path(directory)
    if not path.is_dir():
        raise NotADirectoryError(f"{directory} is not a valid directory.")

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(get_recursive_size, item): item for item in path.glob('*')}
        sizes = {future.result(): path for future, path in futures.items()}

    sorted_items = sorted(sizes.items(), reverse=True)
    selected_items = []
    for size, item in sorted_items:
        if byte_limit >= size:
            byte_limit -= size
            selected_items.append((item, size))
        if byte_limit <= 0:
            break

    for item, size in selected_items:
        print(f"{humanize.naturalsize(size, binary=True)}\t{item}")


if __name__ == "__main__":
    parser = argparse_utils.ArgumentParser(
        description="Select the largest directories/files that fit into a given byte limit."
    )
    parser.add_argument("size_limit")
    parser.add_argument("directory", type=str, help="Directory to scan")
    args = parser.parse_args()

    args.byte_limit = nums.human_to_bytes(args.size_limit)

    main(args.directory, args.byte_limit)
