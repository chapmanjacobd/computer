#!/usr/bin/python3
import os
import shutil
from pathlib import Path

from xklb.utils import argparse_utils

EXCLUDED_EXTENSIONS = {".rar", ".exe", ".sfv"}


def is_excluded_file(file_path):
    suffix = file_path.suffix.lower()
    return suffix in EXCLUDED_EXTENSIONS or (suffix.startswith(".r") and suffix[2:].isdigit())


def dir_suffix(p, suffix):
    return p.with_name(p.name + suffix)


def move_files(args):
    base_dir = Path(args.base_dir)

    for dir_path in sorted(base_dir.glob("*")):
        if dir_path.is_dir():
            for p in sorted(dir_path.rglob("*")):
                if p.is_file() and not is_excluded_file(p):
                    destination_path = base_dir / dir_suffix(dir_path, p.suffix)

                    if destination_path.exists():
                        if destination_path.parent.parent != base_dir:
                            extended_suffix = '.' + p.parent.parent.name + p.suffix
                            destination_path = base_dir / dir_suffix(dir_path, (extended_suffix.replace('..', '.')))
                            if destination_path.exists():
                                extended_suffix = '.' + p.parent.name + p.suffix
                                destination_path = base_dir / dir_suffix(dir_path, (extended_suffix.replace('..', '.')))
                        else:
                            extended_suffix = '.' + p.parent.name + p.suffix
                            destination_path = base_dir / dir_suffix(dir_path, (extended_suffix.replace('..', '.')))

                    counter = 1
                    while destination_path.exists():
                        extended_suffix = f'.{counter}' + p.suffix
                        destination_path = base_dir / dir_suffix(dir_path, (extended_suffix))

                    if not args.dry_run:
                        shutil.move(str(p), str(destination_path))
                    print(f"Moved {p} to {destination_path}")


def main():
    parser = argparse_utils.ArgumentParser(
        description="Move files in each directory to the cwd with a specific naming convention."
    )
    parser.add_argument("--dry-run", action='store_true')
    parser.add_argument("base_dir", nargs="?", default=os.getcwd(), help="The base directory to start the search.")
    args = parser.parse_args()

    move_files(args)


if __name__ == "__main__":
    main()
