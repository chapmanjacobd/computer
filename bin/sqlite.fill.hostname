#!/usr/bin/python3
import argparse
import sqlite3
from urllib.parse import urlparse


def parse_args():
    parser = argparse.ArgumentParser(description="Extract hostnames from URLs.")
    parser.add_argument("db_path")
    parser.add_argument("-t", "--table", default="media")
    return parser.parse_args()


def clean_url_to_hostname(args):
    config = {
        "db": args.db_path,
        "query_select": f"SELECT id, path FROM {args.table} WHERE hostname IS NULL OR hostname = ''",
        "query_update": f"UPDATE {args.table} SET hostname = ? WHERE id = ?",
    }

    conn = sqlite3.connect(config["db"])
    cursor = conn.cursor()

    cursor.execute(config["query_select"])
    rows = cursor.fetchall()

    updates = []
    for row_id, raw_url in rows:
        if raw_url:
            # urlparse("https://gemini.google.com/app") -> netloc="gemini.google.com"
            parsed_url = urlparse(raw_url)
            hostname = parsed_url.netloc or parsed_url.path.split("/")[0]
        else:
            hostname = "unknown.domain"

        updates.append((hostname, row_id))

    if updates:
        cursor.executemany(config["query_update"], updates)
        conn.commit()

    conn.close()


if __name__ == "__main__":
    args = parse_args()
    clean_url_to_hostname(args)
