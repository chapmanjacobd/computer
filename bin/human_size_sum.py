#!/usr/bin/python3
import sys

import humanize
from library.utils import nums

total = 0
for line in sys.stdin:
    total += float(nums.human_to_bytes(line))

print(f"Total: {humanize.naturalsize(total)}")
