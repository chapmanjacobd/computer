#!/usr/bin/python3
import argparse
import itertools
import shlex
import shutil
import sys
from collections.abc import Iterable, Iterator

import duckdb
from tabulate import tabulate

TERMINAL_SIZE = shutil.get_terminal_size(fallback=(150, 50))


def extended_view(iterable):
    print_index = True
    if isinstance(iterable, dict):
        print_index = False
        iterable = [iterable]

    if hasattr(iterable, "__iter__") and not hasattr(iterable, "__len__"):  # generator
        try:
            first_item = next(iter(iterable))
        except StopIteration:
            return  # if the generator is empty, return early
        iterable = itertools.chain([first_item], iterable)
        max_key_length = max(len(key) for key in first_item.keys())
    else:
        max_key_length = max(len(key) for item in iterable for key in item.keys())

    for index, item in enumerate(iterable, start=1):
        if print_index:
            print(f"-[ RECORD {index} ]-------------------------------------------------------------")
        for key, value in item.items():
            formatted_key = f"{key.ljust(max_key_length)} |"
            print(formatted_key, value)
        if print_index:
            print()


def table(tbl, **kwargs) -> None:
    table_text = tabulate(tbl, tablefmt="simple", headers="keys", showindex=False, **kwargs)
    if not table_text:
        return

    longest_line = max(len(s) for s in table_text.splitlines())
    try:
        if longest_line > TERMINAL_SIZE.columns:
            extended_view(tbl)
        else:
            print(table_text)
    except BrokenPipeError:
        sys.stdout = None
        sys.exit(141)


def flatten(xs: Iterable) -> Iterator:
    for x in xs:
        if isinstance(x, dict):
            yield x
        elif isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
            yield from flatten(x)
        elif isinstance(x, bytes):
            yield x.decode("utf-8")
        else:
            yield x


class ArgparseList(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        items = getattr(namespace, self.dest, None) or []

        if isinstance(values, str):
            items.extend(values.split(","))  # type: ignore
        else:
            items.extend(flatten(s.split(",") for s in values))  # type: ignore

        setattr(namespace, self.dest, items)


def build_query(args):
    table_name = args.table
    conditions = []
    select_parts = ["*"]

    if args.include:
        include_conditions = []
        include_scores = []
        for word in args.include:
            if args.min_include is not None:
                cond = f"fts_main_{table_name}.match_bm25(path, '{word}') >= {args.min_include}"
            else:
                cond = f"fts_main_{table_name}.match_bm25(path, '{word}') IS NOT NULL"
            include_conditions.append(cond)
            include_scores.append(f"fts_main_{table_name}.match_bm25(path, '{word}')")
        conditions.append("\n(" + "\n OR ".join(include_conditions) + ")")

        if args.score:
            include_sum = " + ".join(include_scores)
            select_parts.append(f"({include_sum}) AS include_score")


    if args.exclude:
        exclude_conditions = []
        exclude_scores = []
        for word in args.exclude:
            if args.max_exclude is not None:
                cond = f"COALESCE(fts_main_{table_name}.match_bm25(path, '{word}'), 0) < {args.max_exclude}"
            else:
                cond = f"fts_main_{table_name}.match_bm25(path, '{word}') IS NULL"
            exclude_conditions.append(cond)
            exclude_scores.append(f"fts_main_{table_name}.match_bm25(path, '{word}')")
        conditions.append("\n(" + "\n AND ".join(exclude_conditions) + ")")

        if args.score:
            exclude_sum = " + ".join(exclude_scores)
            select_parts.append(f"({exclude_sum}) AS exclude_score")

    where_clause = "\n WHERE " + " AND ".join(conditions) if conditions else ""
    select_clause = ", ".join(select_parts)
    query = f"SELECT {select_clause}\n FROM {table_name}{where_clause}"
    return query


def main():
    parser = argparse.ArgumentParser(
        description="Search columns in a DuckDB table with optional include/exclude words and score thresholds"
    )
    parser.add_argument("--include", "-s", nargs="+", help="Words to include in the search")
    parser.add_argument("--exclude", "-E", nargs="+", help="Words to exclude from the search")
    parser.add_argument("--score", action='store_true', help="Calculate match score")
    parser.add_argument("--min-include", type=float, help="Minimum score threshold for include words")
    parser.add_argument("--max-exclude", type=float, help="Maximum score threshold for exclude words")
    parser.add_argument("--create-index", '--create', action='store_true', help="Create or recreate the fts index")
    parser.add_argument("--limit", '-l', '-L', type=int, default=40, help="Limit printed rows")

    parser.add_argument("database", help="Database to query")
    parser.add_argument("table", help="Table to query")
    parser.add_argument("--pk", required=True, help="Column to use as pk")
    parser.add_argument("columns", action=ArgparseList, help="Columns to search")
    args = parser.parse_args()

    if any(s in args.table for s in ['\\', '/', '.parquet']):
        raise TypeError("fts requires duckdb format. Parquet will not work")

    if args.include:
        args.include = [s.replace("'", "\'") for s in args.include]
    if args.exclude:
        args.exclude = [s.replace("'", "\'") for s in args.exclude]

    conn = duckdb.connect(database=args.database or ':memory:')
    if args.create_index:
        columns_for_fts = ", ".join([f"'{col}'" for col in args.columns])
        conn.execute(f"PRAGMA create_fts_index('{args.table}', '{args.pk}', {columns_for_fts}, overwrite=1);")
        if not any([args.include, args.exclude]):
            raise SystemExit(0)

    query = build_query(args)
    print("Generated Query:", query)

    result = conn.execute(query).df()
    count = len(result)
    if args.limit and count > args.limit:
        result = result.sample(n=args.limit)

    table(result.to_dict(orient='records'))
    print(count, 'matches')


if __name__ == "__main__":
    main()
