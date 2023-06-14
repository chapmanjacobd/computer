#!/usr/bin/python
# ~/bin/sleepy_run.py "429 Too Many Requests" yes 429 Too Many Requests

import argparse
import sys
import signal
import subprocess
import time


def sleep_proc(args, process):
    process.send_signal(signal.SIGTSTP)
    print("Program paused")

    time.sleep(args.time)

    process.send_signal(signal.SIGCONT)
    print("Program resumed")


def sleepy_run(args):
    process = subprocess.Popen(args.program, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    while process.poll() is None:
        line = process.stdout.readline()
        if line is None:
            break

        sys.stdout.buffer.write(line)
        for b in args.trigger:
            if b in line:
                sleep_proc(args, process)
                break


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run a program and pause it when a specific error message is encountered."
    )
    parser.add_argument("--time", "-t", default=10 * 60, type=int, help="Seconds to sleep for")
    parser.add_argument("--trigger", action='append', help="Error message to monitor for")
    parser.add_argument("program", nargs="+", help="Program command and arguments")
    args = parser.parse_args()

    if not args.trigger:
        args.trigger = ['429 Too Many Requests', 'Bad Request', 'Rate limit']
    args.trigger = [s.encode() for s in args.trigger]

    sleepy_run(args)
