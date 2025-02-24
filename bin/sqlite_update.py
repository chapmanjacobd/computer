#!/usr/bin/env python3

import os
import sqlite3
import sys

from library.utils import arggroups, argparse_utils, consts, iterables


def update_database(db_path, table, pk_column, pks, data):
    try:
        conn = sqlite3.connect(db_path)
        with conn:
            cursor = conn.cursor()

            modified_row_count = 0
            pks_chunked = iterables.chunks(pks, consts.SQLITE_PARAM_LIMIT)
            for chunk_pks in pks_chunked:
                placeholders = ",".join(["?"] * len(chunk_pks))
                sql = f"""UPDATE {table} SET {data} WHERE {pk_column} IN ({placeholders})"""
                cursor.execute(sql, tuple(chunk_pks))
                modified_row_count += cursor.rowcount

            conn.commit()
    finally:
        if 'conn' in locals() and conn:
            conn.close()


if __name__ == "__main__":
    parser = argparse_utils.ArgumentParser()
    parser.add_argument("--pk", default="path", help="Primary key column")
    arggroups.debug(parser)

    parser.add_argument("database", help="Path to the SQLite database file")
    parser.add_argument("table", help="Table name")
    parser.add_argument("data", help="Key=Value data to update (SQL injection allowed)")
    args = parser.parse_args()

    if not os.path.exists(args.database):
        print(f"Error: Database file '{args.database}' not found.")
        sys.exit(1)

    pks = [line.strip() for line in sys.stdin]
    update_database(args.database, args.table, args.pk, pks, args.data)
