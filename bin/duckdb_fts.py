#!/usr/bin/python3
import argparse

import duckdb
from library.utils import arggroups, argparse_utils, printing


def build_query(table_name, include_words=None, exclude_words=None):
    conditions = []

    if include_words:
        include_conditions = []
        for word in include_words:
            include_conditions.append(f"fts_main_media.match_bm25(path, '{word}') IS NOT NULL")
        conditions.append("\n(" + "\n OR ".join(include_conditions) + ")")

    if exclude_words:
        exclude_conditions = []
        for word in exclude_words:
            exclude_conditions.append(f"fts_main_media.match_bm25(path, '{word}') IS NULL")
        conditions.append("\n(" + "\n AND ".join(exclude_conditions) + ")")

    if conditions:
        where_clause = "\n WHERE " + " AND ".join(conditions)
    else:
        where_clause = ""

    query = f"SELECT * FROM {table_name}{where_clause}"
    return query


def main():
    parser = argparse.ArgumentParser(
        description="Search columns in a DuckDB table with optional include/exclude words."
    )
    parser.add_argument("-E", "--exclude", nargs="+", help="Words to exclude from the search")
    parser.add_argument("-s", "--include", nargs="+", help="Words to include in the search")
    parser.add_argument("--create-index", '--create', action='store_true', help="Create or recreate the fts index")
    arggroups.debug(parser)

    parser.add_argument("database", help="Database to query")
    parser.add_argument("table", help="Table to query")
    parser.add_argument("--pk", required=True, help="Column to use as pk")
    parser.add_argument("columns", action=argparse_utils.ArgparseList, help="Columns to search")
    args = parser.parse_args()

    if any(s in args.table for s in ['\\', '/', '.parquet']):
        raise ValueError("fts requires duckdb format. Parquet will not work")

    conn = duckdb.connect(database=args.database or ':memory:')
    if args.create_index:
        columns_for_fts = ", ".join([f"'{col}'" for col in args.columns])
        conn.execute(f"PRAGMA create_fts_index('{args.table}', '{args.pk}', {columns_for_fts}, overwrite=1);")

    query = build_query(args.table, args.include, args.exclude)
    print("Generated Query:", query)

    result = conn.execute(query).df()
    count = len(result)
    result = result.sample(n=40)

    printing.table(result.to_dict(orient='records'))
    print(count, 'matches')


if __name__ == "__main__":
    main()
