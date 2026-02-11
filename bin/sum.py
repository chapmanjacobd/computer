#!/usr/bin/python3
import argparse
import sys


def sum_column(args):
    total = 0.0

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        # If delimiter is None (default), split() handles any whitespace
        parts = line.split(args.delimiter)

        try:
            val_str = parts[args.column].replace(',', '')
            total += float(val_str)
        except (IndexError, ValueError):
            continue

    print(f"{total:,.2f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sum a specific column from stdin.")
    parser.add_argument(
        "-c",
        "--column",
        type=int,
        default=-1,
        help="Column index to sum (0-based, or negative for right-to-left. Default: -1)",
    )
    parser.add_argument("-d", "--delimiter", default=None, help="Field delimiter (default: any whitespace)")

    args = parser.parse_args()
    sum_column(args)
