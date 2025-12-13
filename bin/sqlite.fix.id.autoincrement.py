#!/usr/bin/env python3

import argparse
import sqlite3
import sys
from pathlib import Path


def fix_table_ids(db_path, table_name, id_column='id'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    if not cursor.fetchone():
        print(f"Error: Table '{table_name}' does not exist in the database.")
        return False

    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()

    id_col_info = None
    for col in columns:
        if col[1] == id_column:
            id_col_info = col
            break
    if not id_col_info:
        print(f"Error: Column '{id_column}' does not exist in table '{table_name}'.")
        return False

    cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {id_column} IS NULL")
    null_count = cursor.fetchone()[0]

    print(f"Database: {db_path}")
    print(f"Table: {table_name}")
    print(f"ID Column: {id_column}")
    print(f"NULL IDs found: {null_count}")

    # Fill NULL ids with sequential values
    if null_count > 0:
        print(f"\nFilling {null_count} NULL id values...")

        # Get the maximum existing id
        cursor.execute(f"SELECT MAX({id_column}) FROM {table_name}")
        max_id = cursor.fetchone()[0] or 0

        # Get rows with NULL ids
        cursor.execute(f"SELECT rowid FROM {table_name} WHERE {id_column} IS NULL")
        null_rows = cursor.fetchall()

        # Update each NULL id
        next_id = max_id + 1
        for row in null_rows:
            cursor.execute(f"UPDATE {table_name} SET {id_column} = ? WHERE rowid = ?", (next_id, row[0]))
            next_id += 1

        conn.commit()
        print(f"✓ Filled {null_count} NULL ids (starting from {max_id + 1})")

    # Recreate table with AUTOINCREMENT
    print(f"\nRecreating table with AUTOINCREMENT on {id_column}...")

    # Build column definitions for new table
    col_defs = []
    for col in columns:
        col_name = col[1]
        col_type = col[2]
        not_null = " NOT NULL" if col[3] else ""
        default = f" DEFAULT {col[4]}" if col[4] is not None else ""

        if col_name == id_column:
            # Make id column INTEGER PRIMARY KEY AUTOINCREMENT
            col_defs.append(f"{col_name} INTEGER PRIMARY KEY AUTOINCREMENT")
        else:
            pk = " PRIMARY KEY" if col[5] else ""
            col_defs.append(f"{col_name} {col_type}{not_null}{default}{pk}")

    temp_table = f"{table_name}_temp"

    # Create temporary table with new schema
    create_stmt = f"CREATE TABLE {temp_table} ({', '.join(col_defs)})"
    cursor.execute(create_stmt)

    # Copy data to temporary table
    col_names = [col[1] for col in columns]
    cursor.execute(
        f"INSERT INTO {temp_table} ({', '.join(col_names)}) " f"SELECT {', '.join(col_names)} FROM {table_name}"
    )

    # Drop original table
    cursor.execute(f"DROP TABLE {table_name}")

    # Rename temporary table
    cursor.execute(f"ALTER TABLE {temp_table} RENAME TO {table_name}")

    conn.commit()
    print(f"✓ Table recreated with AUTOINCREMENT on {id_column}")

    # Verify changes
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    total_rows = cursor.fetchone()[0]
    print(f"\n✓ Success! Table now has {total_rows} rows with autoincrement id.")

    conn.close()
    return True



def main():
    parser = argparse.ArgumentParser(
        description="Fix SQLite table to make id column autoincrement and fill NULL ids.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s database.db users
  %(prog)s database.db products --id-column product_id
        """,
    )
    parser.add_argument('--id-column', type=str, default='id', help='Name of the id column (default: id)')

    parser.add_argument('database', type=str, help='Path to the SQLite database file')
    parser.add_argument('table', type=str, help='Name of the table to fix')
    args = parser.parse_args()

    db_path = Path(args.database)
    if not db_path.exists():
        print(f"Error: Database file '{args.database}' does not exist.", file=sys.stderr)
        sys.exit(1)

    # Fix the table
    success = fix_table_ids(args.database, args.table, args.id_column)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
