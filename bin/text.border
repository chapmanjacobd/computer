#!/usr/bin/env -S python -S

import sys


text = ' '.join(sys.argv[1:])
c = '#'
if len(c) != 1:
    print('Error: symbol argument must be a single character')
    sys.exit(1)

above = 4 + len(text) + 4
print(c * above)
print(f'{c*2}  {text}  {c*2}')
print(c * above)
