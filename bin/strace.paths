#!/usr/bin/python3
import re
import sys

filepath_pattern = re.compile(r'\"(.*?)\"')


def process_line(line):
    filepath = filepath_pattern.findall(line)
    if filepath:
        print(filepath[0], file=sys.stderr if line.endswith('ENOENT (No such file or directory)\n') else sys.stdout)


for line in sys.stdin:
    process_line(line)
