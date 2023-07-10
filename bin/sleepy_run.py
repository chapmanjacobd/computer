#!/usr/bin/python
# ~/bin/sleepy_run.py --trigger "429 Too Many Requests" yes 429 Too Many Requests

import argparse
import random
import signal
import subprocess
import sys
import time


class Actions:
    sleep = 'sleep'
    signal = 'signal'


def sleep_proc(args, process):
    process.send_signal(signal.SIGTSTP)
    print("Program paused")

    time.sleep(args.time or (random.uniform(3.0, 10.0) * 60))

    process.send_signal(signal.SIGCONT)
    print("Program resumed")


def signal_proc(args, process):
    process.send_signal(args.exit_signal)


def sleepy_run(args):
    process = subprocess.Popen(args.program, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    while process.poll() is None:
        line = process.stdout.readline()
        if line is None:
            break

        sys.stdout.buffer.write(line)
        for b in args.trigger:
            if b in line:
                if args.action == 'sleep':
                    sleep_proc(args, process)
                elif args.action == 'signal':
                    signal_proc(args, process)
                break

    sys.exit(process.wait())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run a program and do something when a specific message is encountered (stdout or stderr)."
    )
    parser.add_argument(
        "--action",
        default=Actions.sleep,
        choices=[Actions.sleep, Actions.signal],
        help="Action to take after trigger",
    )
    parser.add_argument(
        "--time", "-T", default=None, type=float, help="Seconds to sleep (for sleep action; default random 3~10 mins)"
    )
    parser.add_argument(
        "--signal", "-s", default="SIGTERM", help="Exit signal to send (for signal action; default SIGTERM)"
    )

    parser.add_argument("--trigger", "-t", action='append', help="Error message to monitor for")
    parser.add_argument("program", nargs="+", help="Program command and arguments")
    args = parser.parse_args()

    args.exit_signal = getattr(signal, args.signal.upper())

    if not args.trigger:
        args.trigger = ['429 Too Many Requests', '429 Unknown', 'Rate limit']
    args.trigger = [s.encode() for s in args.trigger]

    sleepy_run(args)
