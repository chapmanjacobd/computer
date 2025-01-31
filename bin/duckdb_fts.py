#!/usr/bin/python3
import argparse

import duckdb
from library.utils import arggroups, argparse_utils, printing


def build_query(table_name, include_words=None, exclude_words=None, min_include=None, max_exclude=None):
    conditions = []
    select_parts = ["*"]

    if include_words:
        include_conditions = []
        include_scores = []
        for word in include_words:
            if min_include is not None:
                cond = f"fts_main_{table_name}.match_bm25(path, '{word}') >= {min_include}"
            else:
                cond = f"fts_main_{table_name}.match_bm25(path, '{word}') IS NOT NULL"
            include_conditions.append(cond)
            include_scores.append(f"fts_main_{table_name}.match_bm25(path, '{word}')")
        conditions.append("\n(" + "\n OR ".join(include_conditions) + ")")
        include_sum = " + ".join(include_scores)
        select_parts.append(f"({include_sum}) AS include_score")
    else:
        include_sum = "0"

    if exclude_words:
        exclude_conditions = []
        exclude_scores = []
        for word in exclude_words:
            if max_exclude is not None:
                cond = f"COALESCE(fts_main_{table_name}.match_bm25(path, '{word}'), 0) < {max_exclude}"
            else:
                cond = f"fts_main_{table_name}.match_bm25(path, '{word}') IS NULL"
            exclude_conditions.append(cond)
            exclude_scores.append(f"fts_main_{table_name}.match_bm25(path, '{word}')")
        conditions.append("\n(" + "\n AND ".join(exclude_conditions) + ")")
        exclude_sum = " + ".join(exclude_scores)
        select_parts.append(f"({exclude_sum}) AS exclude_score")
    else:
        exclude_sum = "0"

    if include_words or exclude_words:
        total_include = include_sum if include_words else "0"
        total_exclude = exclude_sum if exclude_words else "0"
        select_parts.append(f"({total_include} - {total_exclude}) AS total_score")

    where_clause = "\n WHERE " + " AND ".join(conditions) if conditions else ""
    select_clause = ", ".join(select_parts)
    query = f"SELECT {select_clause} FROM {table_name}{where_clause}"
    return query


def main():
    parser = argparse.ArgumentParser(
        description="Search columns in a DuckDB table with optional include/exclude words and score thresholds."
    )
    parser.add_argument("-E", "--exclude", nargs="+", help="Words to exclude from the search")
    parser.add_argument("-s", "--include", nargs="+", help="Words to include in the search")
    parser.add_argument("--min-include", type=float, help="Minimum score threshold for include words (use >= instead of IS NOT NULL)")
    parser.add_argument("--max-exclude", type=float, help="Maximum score threshold for exclude words (use < instead of IS NULL)")
    parser.add_argument("--create-index", '--create', action='store_true', help="Create or recreate the fts index")
    parser.add_argument("--limit", '-l', '-L', type=int, default=40, help="Limit printed rows")
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

    query = build_query(args.table, args.include, args.exclude, args.min_include, args.max_exclude)
    print("Generated Query:", query)

    result = conn.execute(query).df()
    count = len(result)
    if args.limit and count > args.limit:
        result = result.sample(n=args.limit)

    printing.table(result.to_dict(orient='records'))
    print(count, 'matches')


if __name__ == "__main__":
    main()
