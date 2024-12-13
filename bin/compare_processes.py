#!/usr/bin/python3

import difflib
import subprocess
from concurrent.futures import ProcessPoolExecutor

from rich import print
from library.utils import argparse_utils

parser = argparse_utils.ArgumentParser()
parser.add_argument('pids', metavar='N', type=int, nargs='+', help='PID(s) to compare')
args = parser.parse_args()


def get_proc_info(pid):
    return {
        'pid': pid,
        'ltrace': subprocess.run(['timeout', '10s', 'ltrace', '-fcp', str(pid)], capture_output=True).stderr.decode(),
    }


with ProcessPoolExecutor() as executor:
    results = executor.map(get_proc_info, args.pids)
results = list(results)

[print(v) for d in results for v in d.values()]

for i in range(len(results)):
    print(f"\nPID {args.pids[i]} vs {args.pids[i-1]}")

    curr_d = results[i]
    prev_d = results[i - 1]

    print("\nltrace diff:")
    print('\n'.join(difflib.unified_diff(prev_d['ltrace'].splitlines(), curr_d['ltrace'].splitlines())))
