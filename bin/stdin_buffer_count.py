#!/usr/bin/python3
import signal
import sys
import time

line_count = 0

def sigpipe_handler(signum, frame):
    print(f"Received SIGPIPE. Total lines: {line_count}")
    sys.exit(141)

signal.signal(signal.SIGPIPE, sigpipe_handler)

try:
    for line in sys.stdin:
        sys.stdout.write(line)
        line_count += 1
        time.sleep(1)
except KeyboardInterrupt:
    print(f"\nTotal lines read: {line_count}")
