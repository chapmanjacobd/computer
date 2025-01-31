#!/usr/bin/python3
import argparse
import shlex

import duckdb
from library.utils import argparse_utils, printing, arggroups


def build_query(table_name, columns, include_words=None, exclude_words=None):
    conditions = []

    if include_words:
        include_conditions = []
        for word in include_words:
            for col in columns:
                include_conditions.append(f"{col} ILIKE '%{word}%'")
        conditions.append("\n(" + "\n OR ".join(include_conditions) + ")")

    if exclude_words:
        exclude_conditions = []
        for word in exclude_words:
            for col in columns:
                exclude_conditions.append(f"{col} NOT ILIKE '%{word}%'")
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
    arggroups.debug(parser)

    parser.add_argument("database", help="Database to query.")
    parser.add_argument("table", help="Table to query.")
    parser.add_argument("columns", action=argparse_utils.ArgparseList, help="Columns to search")
    args = parser.parse_args()

    if any(s in args.table for s in ['\\', '/', '.parquet']):
        args.table = "'" + shlex.quote(args.table) + "'"

    query = build_query(args.table, args.columns, args.include, args.exclude)
    print("Generated Query:", query)

    conn = duckdb.connect(database=args.database or ':memory:')
    result = conn.execute(query).df()
    count = len(result)
    result = result.sample(n=40)

    printing.table(result.to_dict(orient='records'))
    print(count, 'matches')


if __name__ == "__main__":
    main()
