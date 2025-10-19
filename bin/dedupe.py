#!/usr/bin/python
import sys

lines_seen = set()
for line in sys.stdin:
    ll = line.lower()
    if ll in lines_seen:
        continue
    lines_seen.add(ll)

    sys.stdout.write(line)
