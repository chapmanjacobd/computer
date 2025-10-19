#!/usr/bin/env python3
import sys


def weighted_interleave(paths):
    files = [open(p, "r", encoding="utf-8", errors="ignore") for p in paths]
    linesets = [f.readlines() for f in files]
    for f in files:
        f.close()

    lengths = [len(lines) for lines in linesets]
    total = sum(lengths)
    if total == 0:
        return
    weights = [l / total for l in lengths]

    indices = [0] * len(linesets)
    n = len(linesets)
    budget = [0.0] * n
    active = True
    while active:
        active = False
        for i, lines in enumerate(linesets):
            if indices[i] >= len(lines):
                continue
            budget[i] += weights[i]

            while budget[i] >= 1.0 and indices[i] < len(lines):
                yield lines[indices[i]].rstrip("\n")
                indices[i] += 1
                budget[i] -= 1.0
            if indices[i] < len(lines):
                active = True


if __name__ == "__main__":
    argv = argv or sys.argv[1:]
    if len(argv) < 2:
        print(f"Usage: {sys.argv[0]} file1 file2 [file3 ...]", file=sys.stderr)
        sys.exit(1)

    for line in weighted_interleave(argv):
        print(line)
