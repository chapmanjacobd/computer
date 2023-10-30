#!/usr/bin/python3
import re
import shlex
import sys
from typing import List

files = sys.stdin.readlines() + ['']

current_group: List[str] = []
for file in files:
    file = file.strip()

    if file:
        current_group.append(file)
    elif file == "":
        if len(current_group) > 1:
            current_group.sort(
                key=lambda x: int(re.search(r"\[(\d+)\]", x).group(1) if re.search(r"\[(\d+)\]", x) else 0),
                reverse=True,
            )
            for f in current_group[1:]:
                print(f"rm {shlex.quote(f)}")
        current_group = []
