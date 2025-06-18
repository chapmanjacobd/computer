#!/usr/bin/env -S python -S

import sys

start_line = int(sys.argv[1])
end_line = int(sys.argv[2])

if start_line < 1 or end_line < start_line:
    sys.stderr.write(f'Error: Invalid line range {start_line}-{end_line}\\n')
    sys.exit(1)

for i, line in enumerate(sys.stdin, 1):
    if start_line <= i <= end_line:
        sys.stdout.write(line)
    elif i > end_line:
        break
