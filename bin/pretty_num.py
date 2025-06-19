#!/usr/bin/env -S python

import argparse
from library.utils import argparse_utils, nums

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sep", "-s", default=",")
    parser.add_argument(
        "numbers", nargs="*", default=argparse_utils.STDIN_DASH, action=argparse_utils.ArgparseArgsOrStdin
    )
    args = parser.parse_args()

    for n in args.numbers:
        n = nums.safe_int_float_str(n)
        print(f'{n:,}'.replace(',', args.sep))
