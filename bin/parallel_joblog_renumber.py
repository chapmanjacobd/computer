#!/usr/bin/python3

import argparse
from xklb.utils import argparse_utils
import sys


def pipe_lines(x) -> None:
    try:
        sys.stdout.writelines(x)
    except BrokenPipeError:
        sys.stdout = None
        sys.exit(141)


parser = argparse_utils.ArgumentParser()
parser.add_argument("joblog", type=argparse.FileType("r"))
parser.add_argument("argsfile", nargs="?", type=argparse.FileType("r"), default=sys.stdin)
parser.add_argument("output_path", nargs="?")
args = parser.parse_args()

joblog = args.joblog.readlines()
args.joblog.close()

argsfile = args.argsfile.readlines()
args.argsfile.close()


new_joblog = ['Seq	Host	Starttime	JobRuntime	Send	Receive	Exitval	Signal	Command']
seq = 1
for argline in argsfile:
    for jobline in joblog:
        if argline.strip() in jobline:
            parts = jobline.split('\t')
            parts[0] = str(seq)
            new_joblog.append("\t".join(parts))
    seq += 1

if args.output_path:
    with open(args.output_path, "w") as output_fd:
        output_fd.writelines(new_joblog)
else:
    pipe_lines(new_joblog)
