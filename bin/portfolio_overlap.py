#!/usr/bin/env python3

import csv
import sys


def load_holdings(path):
    holdings = {}

    with open(path, newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            if not row:
                continue

            symbol = row.get("Symbol")
            percent = row.get("Percent of Assets")

            # Skip rows with missing data
            if not symbol or not percent:
                continue

            symbol = symbol.strip()
            if symbol == "":
                continue

            try:
                percent = float(percent)
            except ValueError:
                continue

            holdings[symbol] = percent

    return holdings


def calculate_overlap(fund_a, fund_b):
    shared_symbols = set(fund_a) & set(fund_b)
    return sum(min(fund_a[s], fund_b[s]) for s in shared_symbols)


def main():
    if len(sys.argv) != 3:
        print("Usage: python overlap.py fund1.csv fund2.csv")
        sys.exit(1)

    fund1 = load_holdings(sys.argv[1])
    fund2 = load_holdings(sys.argv[2])

    overlap_percent = calculate_overlap(fund1, fund2)

    print(f"Weight-based overlap: {overlap_percent:.4f}%")
    print(f"Shared symbols: {len(set(fund1) & set(fund2))}")
    print(f"Fund1 holdings: {len(fund1)}")
    print(f"Fund2 holdings: {len(fund2)}")


if __name__ == "__main__":
    main()