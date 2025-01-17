#!/usr/bin/python3
import sqlite3
import time

import sqlite_utils
from library.utils import printing


def get_max_rowids(db: sqlite_utils.Database):
    tables = db.table_names()

    max_rowids = {}
    for table_name in tables:
        cursor = db.execute(f"SELECT MAX(rowid) FROM {table_name};")
        max_rowid = cursor.fetchone()[0]
        max_rowids[table_name] = max_rowid

    return max_rowids


def print_new_rows(db, max_rowids):
    for table_name, last_max_rowid in max_rowids.items():
        new_rows = list(
            db.query(f"SELECT rowid as rowid, * FROM {table_name} WHERE rowid > ? ORDER BY rowid;", (last_max_rowid or 0,))
        )
        if new_rows:
            print(f"{table_name}:")
            printing.table(new_rows)

            max_rowids[table_name] = max(row['rowid'] for row in new_rows)


def main(db_path):
    db = sqlite_utils.Database(sqlite3.connect(f"file:{db_path}?mode=ro", uri=True))

    max_rowids = get_max_rowids(db)

    try:
        while True:
            print_new_rows(db, max_rowids)
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        db.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python sqlite_tail.py <database_path>")
        sys.exit(1)

    db_path = sys.argv[1]
    main(db_path)
