#!/usr/bin/python3
import sqlite3
import time

import sqlite_utils
from library.utils import argparse_utils, printing


def get_initial_rowids(args):
    tables = args.db.table_names()

    max_rowids = {}
    for table_name in tables:
        if table_name in ['sqlite_stat1'] or '_fts' in table_name:
            continue

        cursor = args.db.execute(f"SELECT MAX(rowid) FROM {table_name};")
        max_rowid = cursor.fetchone()[0]
        max_rowids[table_name] = max_rowid or 0

    return max_rowids


def print_new_rows(args, max_rowids):
    for table_name, max_rowid in max_rowids.items():
        # `rowid as rowid` is required due to SQLite rewriting the "rowid"
        # in the query/resultset with any rowid-equivalent (auto-incremental column name)
        new_rows = list(
            args.db.query(f"SELECT rowid as rowid, * FROM {table_name} WHERE rowid > ? ORDER BY rowid;", (max_rowid,))
        )
        if new_rows:
            print(f"{table_name}:")
            printing.table(new_rows)

            max_rowids[table_name] = max(row['rowid'] for row in new_rows)

    return max_rowids


def sqlite_tail(db_path):
    args.db = sqlite_utils.Database(sqlite3.connect(f"file:{db_path}?mode=ro", uri=True))

    max_rowids = get_initial_rowids(args)

    try:
        while True:
            max_rowids = print_new_rows(args, max_rowids)
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        args.db.close()


if __name__ == "__main__":
    parser = argparse_utils.ArgumentParser()
    parser.add_argument("database")
    args = parser.parse_args()

    sqlite_tail(args.database)
