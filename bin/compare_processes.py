#!/usr/bin/python3

import argparse
from concurrent.futures import ProcessPoolExecutor
import difflib
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('pids', metavar='N', type=int, nargs='+', help='PID(s) to compare')
args = parser.parse_args()


def get_proc_info(pid):
    lsof = subprocess.run(['lsof', '-b', '-p', str(pid)], capture_output=True).stdout.decode()
    pstree = subprocess.run(['pstree', '-p', str(pid)], capture_output=True).stdout.decode()
    strace = subprocess.run(['timeout', '10s', 'strace', '-p', str(pid)], capture_output=True).stdout.decode()
    ltrace = subprocess.run(['timeout', '10s','ltrace', '-p', str(pid)], capture_output=True).stdout.decode()

    return {
        'lsof': lsof,
        'pstree': pstree,
        'strace': strace,
        'ltrace': ltrace,
    }


with ProcessPoolExecutor() as executor:
    results = executor.map(get_proc_info, args.pids)

results = list(results)
for i in range(len(results)):
    print(f"\nPID {args.pids[i]} vs {args.pids[i-1]}")

    curr_d = results[i]
    prev_d = results[i - 1]

    print("\nlsof diff:")
    print('\n'.join(difflib.unified_diff(prev_d['lsof'].splitlines(), curr_d['lsof'].splitlines())))

    print("\npstree diff:")
    print('\n'.join(difflib.unified_diff(prev_d['pstree'].splitlines(), curr_d['pstree'].splitlines())))

    print("\nstrace diff:")
    print('\n'.join(difflib.unified_diff(prev_d['strace'].splitlines(), curr_d['strace'].splitlines())))

    print("\nltrace diff:")
    print('\n'.join(difflib.unified_diff(prev_d['ltrace'].splitlines(), curr_d['ltrace'].splitlines())))
