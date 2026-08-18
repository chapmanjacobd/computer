#!/usr/bin/env python3
import argparse
import csv
import sys

from bs4 import BeautifulSoup
from library.utils import argparse_utils, printing, web


def extract_tables(args, url):
    writer = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")

    resp = web.get(args, url)
    if resp is None:
        return

    soup = BeautifulSoup(resp.text, "html.parser")

    tables = soup.find_all("table")  # , {"class": "wikitable"}
    for idx, table in enumerate(tables, start=1):
        headers = [th.get_text(strip=True) for th in table.find_all("th")]
        matching = [h for h in headers if h in args.columns]

        if not matching:
            print(
                f"[WARN] Table {idx} on {url} has no matching columns",
                file=sys.stderr,
            )
            rows = table.find_all("tr")
            if len(rows) >= 1:
                first_row = [td.get_text(strip=True) for td in rows[1].find_all(["td", "th"])]
                example = dict(zip(headers, first_row))
                printing.table([example], file=sys.stderr)
            continue

        # header -> index
        col_idx = {h: i for i, h in enumerate(headers) if h in matching}
        if args.headers:
            writer.writerow(matching)

        for row in table.find_all("tr")[1:]:
            cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
            if len(cells) < len(headers):
                continue
            row_data = [cells[col_idx[h]] for h in matching]
            writer.writerow(row_data)


def main():
    parser = argparse.ArgumentParser(description="Extract specific columns from MediaWiki tables.")
    parser.add_argument("urls", nargs="+", help="MediaWiki page URLs")
    parser.add_argument(
        "--columns", nargs="+", action=argparse_utils.ArgparseList, required=True, help="Column names to extract"
    )
    parser.add_argument("--headers", action="store_true", help="Print headers for each table")
    args = parser.parse_args()

    for url in args.urls:
        extract_tables(args, url)


if __name__ == "__main__":
    main()
