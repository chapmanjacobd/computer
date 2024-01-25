#!/usr/bin/python3
import argparse
import sqlite3
from sqlite_utils import Database

def strip_enclosing_quotes(s):
    if len(s) < 2:
        return s

    if (s[0] == '"' and s[-1] == '"') or (s[0] == "'" and s[-1] == "'"):
        return s[1:-1]

    return s

def process_columns(db_path, columns):
    db = Database(sqlite3.connect(db_path))

    for table in db.tables:
        columns_to_update = [col for col in columns if col in table.columns_dict]
        if not columns_to_update:
            continue

        print(table)
        print(columns_to_update)

        for row in table.rows:
            updates = {col: strip_enclosing_quotes(row[col]) for col in columns_to_update if row[col] != strip_enclosing_quotes(row[col])}
            if updates:
                table.update(row["id"], updates)

def main():
    parser = argparse.ArgumentParser(description="Strip enclosing quotes from specified columns in a SQLite database.")
    parser.add_argument("db_path", help="Path to the SQLite database file")
    parser.add_argument("columns", nargs="+", help="Column names to process")
    args = parser.parse_args()

    process_columns(args.db_path, args.columns)

if __name__ == "__main__":
    main()

