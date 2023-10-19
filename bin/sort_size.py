#!/usr/bin/python3

import os
import sys


def pipe_lines(x) -> None:
    try:
        sys.stdout.writelines(x)
    except BrokenPipeError:
        sys.stdout = None
        sys.exit(141)


def main():
    paths = [line.strip() for line in sys.stdin]
    filtered_paths = filter(os.path.exists, paths)
    sorted_paths = sorted(filtered_paths, key=os.path.getsize, reverse=True)
    pipe_lines('\n'.join(sorted_paths))


if __name__ == "__main__":
    main()
