#!/usr/bin/python3
import sys
import difflib
from typing import Dict, List

groups: Dict[str, List[str]] = {}
for curr in sys.stdin:
    curr = curr.strip()

    is_duplicate = False
    for prev in groups.keys():
        if difflib.SequenceMatcher(None, curr, prev).ratio() > 0.73:
            groups[prev].append(curr)
            is_duplicate = True
            break

    if not is_duplicate:
        groups[curr] = []

for key, group in groups.items():
    if len(group) >= 1:
        print(key)
        for dupe in group:
            print(dupe)
        print()
