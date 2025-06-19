#!/usr/bin/env -S python -S

import sys

n = sys.stdin.read()
s = f'{n:,}'.replace(',', '$sep')
print(s)
