#!/usr/bin/env python3

import sys

def sort_by_folder_len(x):
    parent, file = x.rsplit('/', 1)
    return (parent.count('/'), parent, file)

def sort_lines(lines):
    sorted_lines = sorted(lines, key=sort_by_folder_len)
    return sorted_lines

def main():
    lines = sys.stdin.readlines()
    sorted_lines = sort_lines(lines)
    for line in sorted_lines:
        print(line, end='')

if __name__ == "__main__":
    main()
