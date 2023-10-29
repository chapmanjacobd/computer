#!/usr/bin/python3
import sys
import difflib
from typing import List

prev_lines: List[str] = []
for curr in sys.stdin:
    curr = curr.strip()

    is_duplicate = False
    for prev in prev_lines:
        if difflib.SequenceMatcher(None, curr, prev).ratio() > 0.73:
            print(prev)
            print(curr)
            is_duplicate = True
            break

    if not is_duplicate:
        prev_lines.append(curr)
