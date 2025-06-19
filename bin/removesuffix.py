#!/usr/bin/env -S python -S

import sys

for line in sys.stdin:
    line = line.rstrip('\r\n')
    for suffix in sys.argv[1:]:
        line = line.removesuffix(suffix)
    print(line)
