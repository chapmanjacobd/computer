#!/usr/bin/env -S python -S

import sys

for line in sys.stdin:
    for prefix in sys.argv[1:]:
        line = line.removeprefix(prefix)
    print(line, end='')
