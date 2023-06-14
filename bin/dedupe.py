#!/usr/bin/python
import sys

lines_seen = set()
for line in sys.stdin.buffer:
    if line in lines_seen:
        continue

    lines_seen.add(line)
    sys.stdout.buffer.write(line)
