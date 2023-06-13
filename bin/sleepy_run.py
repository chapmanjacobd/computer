#!/usr/bin/python
# ~/bin/sleepy_run.py "429 Too Many Requests" yes 429 Too Many Requests

import argparse
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
    process = subprocess.Popen(args.program)

    while True:
        if process.poll() is None:
            sleep_proc(args, process)

            if process.stdout:
                for line in process.stdout:
                    if args.error_message in line:
                        sleep_proc(args, process)
            if process.stderr:
                for line in process.stderr:
                    if args.error_message in line:
                        sleep_proc(args, process)

        else:
            print("Program exited")
            break
        time.sleep(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run a program and pause it when a specific error message is encountered."
    )
    parser.add_argument("--time", "-t", default=10 * 60, help="Seconds to sleep for")

    parser.add_argument("error_message", help="Error message to monitor for")
    parser.add_argument("program", nargs="+", help="Program command and arguments")
    args = parser.parse_args()

    sleepy_run(args)
