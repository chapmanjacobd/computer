#!/usr/bin/python3

import sys

key_order = [
    'esc', 'f1','f2','f3','f4','f5','f6','f7','f8','f9','f10','f11','f12','del',
    '`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'bs',
    '~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+',
    'q', 'w', 'f', 'p', 'b', 'j', 'l', 'u', 'y', ';', ':', '[','{', ']', '}', '\\', '|',
    'a', 'r', 's', 't', 'g', 'm', 'n', 'e', 'i', 'o', "'", '"',
    'z', 'x', 'c', 'd', 'v', 'b', 'h', 'j', 'k', 'l', ',', '<', '.', '>', '/', '?',
    'space', 'left', 'up', 'down', 'right', 'home','pgup','pgdwn','pgdn','end',
    'prev', 'play', 'playpause', 'next', 'stop'
]

def key_index(key):
    try:
        return key_order.index(key.lower())
    except ValueError:
        # Return a value larger than any valid index for unknown keys
        return len(key_order)

def rw_io(fn):
    sys.stdout.writelines(fn(sys.stdin.readlines()))

def sorter(line):
    s = line.split(' ')[0]
    if not s == '+':
        s = s.split("+")[-1].strip().lower()
        if s == '':
            s = '+'

    return key_index(s)

rw_io(lambda lines: sorted(lines, key=sorter))
