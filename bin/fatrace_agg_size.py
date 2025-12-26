#!/usr/bin/env python3
import argparse
import os
import shutil
import signal
import subprocess
import time

from library.utils import nums, strings
from library.utils.printing import MultilineOverwriteConsole

parser = argparse.ArgumentParser(description="Track file modifications with fatrace and show size deltas.")
parser.add_argument(
    "interval",
    nargs="?",
    type=int,
    default=5,
    help="Refresh interval in seconds (default: 5)",
)
parser.add_argument(
    "--sort",
    default="time_modified:desc",
    help="Sort mode: time_created[:desc], time_modified[:desc], size[:desc]",
)
parser.add_argument(
    "-E",
    "--exclude",
    action="append",
    default=[],
    metavar="SUBSTRING",
    help="Exclude files whose path contains this substring (can be used multiple times)",
)
parser.add_argument("--min-size", help="Exclude files whose size is smaller than this")
parser.add_argument("--min-delta", help="Exclude files whose size delta (+/-) is smaller than this")
args = parser.parse_args()

sort_field, _, sort_dir = args.sort.partition(":")
sort_desc = sort_dir.lower() == "desc"

min_size = nums.human_to_bytes(args.min_size) if args.min_size else 0
min_delta = nums.human_to_bytes(args.min_delta) if args.min_delta else 0

TERMINAL = shutil.get_terminal_size((80, 24))
TERMINAL_LINES = TERMINAL.lines - 3
TERMINAL_WIDTH = TERMINAL.columns - 11

files = {}  # path -> (initial_size, current_size)
last_seen = {}  # path -> last modified time
stop = False


def sigint_handler(sig, frame):
    global stop
    stop = True


signal.signal(signal.SIGINT, sigint_handler)


def should_exclude(path: str) -> bool:
    for substr in args.exclude:
        if substr in path:
            return True
    return False


def get_sort_key(path: str):
    if sort_field == "time_created":
        try:
            return os.path.getctime(path)
        except OSError:
            return 0
    elif sort_field == "time_modified":
        return last_seen.get(path, 0)
    elif sort_field == "size":
        init, cur = files.get(path, (0, 0))
        return cur - init
    return last_seen.get(path, 0)


def sort_files():
    valid_paths = [p for p in last_seen.keys() if not should_exclude(p)]
    return sorted(valid_paths, key=get_sort_key, reverse=sort_desc)


console = MultilineOverwriteConsole()


def print_status(final=False):
    console.reset()

    recent = sort_files()
    count = 0
    for path in recent:
        init, cur = files[path]
        delta = cur - init
        if delta < min_delta:
            continue
        sign = "+" if delta > 0 else "-"
        console.print(f"{sign}{strings.file_size(abs(delta)):<9}{path[0:TERMINAL_WIDTH]}")
        count += 1
        if not final and count >= TERMINAL_LINES:
            break

    console.print(f"{len(recent)} total modified files")
    console.flush()


proc = subprocess.Popen(
    ["sudo", "fatrace", "-f", "W"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, bufsize=1
)

try:
    last_refresh = time.time()

    while not stop:
        line = proc.stdout.readline()
        if not line:
            break

        parts = line.strip().split(" ", 2)
        if len(parts) < 3:
            continue

        _, op, path = parts
        path = path.strip()

        if should_exclude(path):
            continue

        if not os.path.isfile(path):
            continue

        try:
            size = os.path.getsize(path)
            if size < min_size:
                continue
        except OSError:
            continue

        if path not in files:
            files[path] = (size, size)
        else:
            init, _ = files[path]
            files[path] = (init, size)

        last_seen[path] = time.time()

        now = time.time()
        if now - last_refresh >= args.interval:
            print_status()
            last_refresh = now
except KeyboardInterrupt:
    pass
finally:
    proc.terminate()
    proc.wait()

    print_status(final=True)
