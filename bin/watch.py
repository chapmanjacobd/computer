#!/usr/bin/python3
import subprocess
import sys
import time

from xklb.utils import argparse_utils


def get_command_output(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    error = result.stderr.strip()
    if error:
        print(error, file=sys.stderr)

    return result.stdout.strip()


def main():
    parser = argparse_utils.ArgumentParser(description='Compare output of a command')
    parser.add_argument('command', nargs='+', help='Command to execute')
    parser.add_argument('--delay', type=float, default=0.2, help='Delay between checks in seconds')
    args = parser.parse_args()

    prev_output = None

    while True:
        output = get_command_output(' '.join(args.command))
        if output != prev_output:
            print(output)
            prev_output = output

        time.sleep(args.delay)


if __name__ == '__main__':
    main()
