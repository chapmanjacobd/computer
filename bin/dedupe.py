#!/usr/bin/python
import sys

lines_seen = set()
for line in sys.stdin:
    if line in lines_seen:
        continue

    lines_seen.add(line)
    sys.stdout.write(line)
