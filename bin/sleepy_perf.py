#!/usr/bin/python3
import os
import time
from collections import defaultdict

from library.utils import argparse_utils


def parse_args():
    parser = argparse_utils.ArgumentParser(description="Aggregate kernel function sleep counts for processes.")
    parser.add_argument("--aggregate-system", '-a', action="store_true", help="Group by system instead of PID.")
    parser.add_argument("--time", '-t', type=float, default=4.1, help="Profiling time")
    return parser.parse_args()


def get_process_data():
    processes = {}
    for pid in os.listdir("/proc"):
        if pid.isdigit():
            try:
                with open(f"/proc/{pid}/cmdline") as f:
                    command = f.read().replace("\0", " ")
                with open(f"/proc/{pid}/wchan") as f:
                    function_name = f.read().strip()

                if function_name == '0':
                    continue

                processes[pid] = {
                    "command": command,
                    "function_name": function_name,
                }
            except FileNotFoundError:
                pass  # Process might have terminated
    return processes


def main():
    args = parse_args()
    counts = defaultdict(lambda: defaultdict(int))
    start_time = time.time()

    while time.time() - start_time < args.time:
        processes = get_process_data()
        for pid, data in processes.items():
            if args.aggregate_system:
                key = data["function_name"]
                counts[key]["count"] += 1
            else:
                key =  f"{data["function_name"]}{pid}{data["command"]}"
                counts[key]["pid"] = pid
                counts[key]["command"] = data["command"]
                counts[key]["function_name"] = data["function_name"]
                counts[key]["count"] += 1
        time.sleep(0.1)

    if args.aggregate_system:
        counts = sorted(counts.items(), key=lambda item: item[1]["count"], reverse=True)
        for key, data in counts:
            print(f"{data['count']}\t{key}")
    else:
        counts = sorted(counts.items(), key=lambda item: (item[1]["command"], item[1]["count"]), reverse=True)
        for key, data in counts:
            print(f"{data['count']}\t{data['function_name']}\t{data['command']}:{data['pid']}")


if __name__ == "__main__":
    main()
