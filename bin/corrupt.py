#!/usr/bin/python
# https://github.com/joshsegall/corrupt

import argparse
from library.utils import argparse_utils
import random
import string
import sys

parser = argparse_utils.ArgumentParser()
parser.add_argument(
    'input', nargs='?', type=argparse.FileType('rb'), default=sys.stdin, help='input file. defaults to stdin'
)
parser.add_argument(
    '-o',
    '--output',
    type=argparse.FileType('wb'),
    default=sys.stdout,
    action='store',
    help='output filename. defaults to stdout',
)
parser.add_argument(
    '-n',
    action='store',
    type=int,
    default=1000000,
    help='''average good bits per error. defaults to 1000000 (10e-6 bit error rate)''',
)
parser.add_argument('-t', '--truncate', action='store', type=int, default=None, help='truncate file after T bytes')
parser.add_argument(
    '-g', '--garbage', action='store', type=int, default=0, help='add G bytes of garbage at the end of the file'
)
parser.add_argument('-a', '--ascii', action='store_true', help='assume ASCII input and enforce ASCII output')
args = parser.parse_args()

nextn = random.randint(0, args.n * 8)
data = args.input.read()
output_data = bytearray()
for chunk_start in range(0, len(data)):
    chunk_end = chunk_start + 1
    chunk = data[chunk_start:chunk_end]
    output_data += chunk

    if chunk_end > nextn:
        k = nextn - chunk_start * 8

        if args.ascii:
            b = random.choice(string.printable).encode()
        else:
            b = bytes([random.randint(0, 255)])

        output_data[-1] = b[0]
        nextn += random.randint(0, 2 * args.n * 8)

    if args.truncate is not None and len(output_data) > args.truncate:
        output_data = output_data[: args.truncate]
        break

random.seed()
while args.garbage > 0:
    if args.ascii:
        b = random.choice(string.printable).encode()
    else:
        b = bytes([random.randint(0, 255)])
    output_data += b
    args.garbage -= 1

args.output.write(output_data)
args.output.close()
