#!/usr/bin/python3
import argparse
import pandas as pd
import sqlite_utils

def convert_dtypes(args):
    input_db = sqlite_utils.Database(args.input_db)
    output_db = sqlite_utils.Database(args.output_db)

    for table_name in input_db.table_names():
        print(f"Processing table: {table_name}")

        df = pd.read_sql_query(f"SELECT * FROM {table_name}", input_db.conn)
        df = df.convert_dtypes()

        output_db[table_name].insert_all(df.to_dict(orient='records', index=False), alter=True)

def main():
    parser = argparse.ArgumentParser(description="Convert SQLite table columns to better data types and save to a new database.")
    parser.add_argument("input_db", help="Path to the input SQLite database")
    parser.add_argument("output_db", help="Path to the output SQLite database")
    args = parser.parse_args()

    convert_dtypes(args)

if __name__ == "__main__":
    main()
