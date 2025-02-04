#!/usr/bin/python3
import argparse
from typing import Dict, List, Tuple

import duckdb
from tabulate import tabulate

SUPPORTED_TYPES = [
    # unsigned
    "UTINYINT",
    "USMALLINT",
    "UINTEGER",
    "UBIGINT",
    "UHUGEINT",
    # signed
    "TINYINT",
    "SMALLINT",
    "INTEGER",
    "BIGINT",
    "HUGEINT",  # 16
    "FLOAT",
    "DECIMAL",  # 8
    "DOUBLE",
    # time
    "TIMESTAMP WITH TIME ZONE",
    "TIMESTAMP",
    "DATE",
    "TIME",
    "INTERVAL",
    # misc
    "BOOLEAN",
    "UUID",
    # strings / bytes
    "VARCHAR",
    "BLOB",
    # "BITSTRING",
]


def show_data_loss(conn: duckdb.DuckDBPyConnection, table_name: str, col_name: str, target_type: str):
    query = f"""WITH loss AS (
            SELECT {col_name}, TRY_CAST({col_name} AS {target_type}) AS {col_name}_{target_type}
            FROM {table_name}
            WHERE {col_name} IS NOT NULL
            AND (
                {col_name}_{target_type} IS NULL
                OR {col_name}_{target_type}::text != {col_name}::text
            )
        )
        SELECT *, COUNT(*) count FROM loss
        GROUP BY 1,2 ORDER BY 3 DESC;
    """
    result = conn.execute(query).fetchall()
    if result:
        from library.utils import printing

        df = conn.execute(query).df()
        printing.table(df.head(50).to_dict(orient='records'))
        if len(df) > 50:
            print("Showing TOP 50 of", len(df), 'distinct values')
    return result


def count_valid_casts(conn: duckdb.DuckDBPyConnection, table_name: str, col_name: str, target_type: str, rows) -> int:
    query = f"""
        SELECT COUNT(*)
        FROM (
            SELECT TRY_CAST({col_name} AS {target_type}) AS casted
            FROM {table_name}
            LIMIT {rows}
        )
        WHERE casted IS NOT NULL;
    """
    result = conn.execute(query).fetchone()
    if result:
        return result[0]
    return 0


def infer_column_types(conn: duckdb.DuckDBPyConnection, table_name: str, rows: int) -> Dict[str, List[Tuple[str, int]]]:
    columns = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    inferred_types = {}

    for col in columns:
        col_name = col[1]
        col_type = col[2]
        col_is_pk = col[5]
        if col_is_pk:
            continue

        print(f"Analyzing column: {col_name}...")
        type_matches = []

        for dtype in SUPPORTED_TYPES:
            valid_rows = count_valid_casts(conn, table_name, col_name, dtype, rows)
            if valid_rows > 1:
                type_matches.append((dtype, valid_rows))

        if type_matches:
            type_matches.sort(key=lambda x: x[1], reverse=True)
            inferred_types[col_name] = type_matches

    return inferred_types


def generate_alter_statements(
    table_name: str, inferred_types: Dict[str, List[Tuple[str, int]]], force: bool = False
) -> List[str]:
    alter_statements = []
    for col_name, matches in inferred_types.items():
        if matches:
            best_match = matches[0][0]  # Use the top match
            if force:
                alter_statements.append(
                    f"ALTER TABLE {table_name} ALTER {col_name} SET DATA TYPE {best_match} "
                    f"USING TRY_CAST({col_name} AS {best_match});"
                )
            else:
                alter_statements.append(f"ALTER TABLE {table_name} ALTER {col_name} TYPE {best_match};")
    return alter_statements


def generate_create_statement(
    table_name: str, inferred_types: Dict[str, List[Tuple[str, int]]], force: bool = False
) -> str:
    column_statements = []
    for col_name, matches in inferred_types.items():
        if matches:
            best_match = matches[0][0]  # Use the top match
            if force:
                column_statements.append(f"TRY_CAST({col_name} AS {best_match})")
            else:
                column_statements.append(f"CAST({col_name} AS {best_match})")

    return f"""CREATE TABLE {table_name} AS (
    SELECT
        {'\n        '.join(column_statements)}
    FROM {table_name}
);"""


def main():
    parser = argparse.ArgumentParser(description="Infer column types and generate ALTER TABLE statements for DuckDB.")
    parser.add_argument("--rows", type=int, default=1000, help="Number of rows to sample for type inference.")
    parser.add_argument(
        "--loss", action="store_true", help="Print records where the type does not match the initial ones"
    )
    parser.add_argument("--force", action="store_true", help="Use TRY_CAST instead of CAST.")

    parser.add_argument("db_file", type=str, help="Path to the DuckDB file.")
    parser.add_argument("table_name", type=str, help="Name of the table to modify.")
    args = parser.parse_args()

    conn = duckdb.connect(args.db_file)

    inferred_types = infer_column_types(conn, args.table_name, args.rows)

    print("\nTop 3 inferred types for each column:")
    for col_name, matches in inferred_types.items():
        print(f"\nColumn: {col_name}")
        print(tabulate(matches[:3], headers=["Type", "Valid Rows"], tablefmt="pretty"))

        if args.loss:
            show_data_loss(conn, args.table_name, col_name, matches[0][0])

    print("\nGenerated CREATE TABLE statement:")
    print(generate_create_statement(args.table_name, inferred_types, args.force))

    alter_statements = generate_alter_statements(args.table_name, inferred_types, args.force)
    print("\nGenerated ALTER TABLE statements:")
    for stmt in alter_statements:
        print(stmt)

    if alter_statements:
        confirm = input("\nDo you want to execute these statements? (y/n): ").strip().lower()
        if confirm == "y":
            for stmt in alter_statements:
                conn.execute(stmt)
            print("Statements executed successfully.")


if __name__ == "__main__":
    main()
