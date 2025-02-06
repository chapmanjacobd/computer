#!/usr/bin/python3
import sqlite3
import os
import argparse

parser = argparse.ArgumentParser(description='Convert SQLite database columns to BLOB type.')
parser.add_argument('sqlite_db_path', help='Path to the SQLite database file.')

args = parser.parse_args()

sqlite_conn = sqlite3.connect(args.sqlite_db_path)
sqlite_cursor = sqlite_conn.cursor()

sqlite_tables_query = "SELECT name FROM sqlite_master WHERE type='table';"
sqlite_cursor.execute(sqlite_tables_query)
sqlite_tables = [row[0] for row in sqlite_cursor.fetchall()]
sqlite_tables = [
    s for s in sqlite_tables if not s.endswith('_fts') and not '_fts_' in s and not s.startswith('sqlite_stat')
]

for table_name in sqlite_tables:
    print(f"Processing table: {table_name}")
    pragma_table_info_query = f"PRAGMA table_info({table_name});"
    sqlite_cursor.execute(pragma_table_info_query)
    column_info = sqlite_cursor.fetchall()
    column_names = [col[1] for col in column_info]

    # Create a new table with BLOB columns
    temp_table_name = f"_temp_{table_name}"
    create_temp_table_statement = f"CREATE TABLE {temp_table_name} ("
    for col_name in column_names:
        create_temp_table_statement += f"{col_name} BLOB, "
    create_temp_table_statement = create_temp_table_statement.rstrip(', ') + ");"

    print(f"  Creating temporary table: {temp_table_name}")
    sqlite_cursor.execute(create_temp_table_statement)

    # Copy data from old table to new table
    column_list = ', '.join(column_names)
    insert_statement = f"INSERT INTO {temp_table_name} ({column_list}) SELECT {column_list} FROM {table_name};"
    print(f"  Copying data to temporary table")
    sqlite_cursor.execute(insert_statement)

    # Drop the original table
    print(f"  Dropping original table: {table_name}")
    sqlite_cursor.execute(f"DROP TABLE {table_name};")

    # Rename the temporary table to the original table name
    print(f"  Renaming temporary table to: {table_name}")
    sqlite_cursor.execute(f"ALTER TABLE {temp_table_name} RENAME TO {table_name};")

sqlite_conn.commit()
sqlite_conn.close()
