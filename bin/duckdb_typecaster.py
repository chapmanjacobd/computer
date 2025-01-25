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
    "INT1",
    "INT2",
    "INT4",
    "INT8",
    "HUGEINT",  # 16
    "FLOAT4",
    "DECIMAL",  # 8
    "FLOAT8",
    # time
    "DATE",
    "TIME",
    "TIMESTAMP",
    "TIMESTAMPTZ",
    "INTERVAL",
    # misc
    "BOOLEAN",
    "UUID",
    # strings / bytes
    "VARCHAR",
    "BLOB",
    "BITSTRING",
]


def count_valid_casts(conn, table_name: str, col_name: str, target_type: str, rows) -> int:
    query = f"""
        SELECT COUNT(*)
        FROM (
            SELECT TRY_CAST({col_name} AS {target_type}) AS casted
            FROM {table_name}
            LIMIT {rows})
        WHERE casted IS NOT NULL;
    """
    result = conn.execute(query).fetchone()
    return result[0]


def infer_column_types(conn, table_name: str, rows: int) -> Dict[str, List[Tuple[str, int]]]:
    """
    Infer column types by attempting to cast to different types and counting valid rows.
    Returns a dictionary with the top 3 matches for each column.
    """
    columns = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    inferred_types = {}

    for col in columns:
        col_name = col[1]
        print(f"Analyzing column: {col_name}...")
        type_matches = []

        for dtype in SUPPORTED_TYPES:
            valid_rows = count_valid_casts(conn, table_name, col_name, dtype, rows)
            type_matches.append((dtype, valid_rows))

        type_matches.sort(key=lambda x: x[1], reverse=True)
        inferred_types[col_name] = type_matches[:3]

    return inferred_types


def generate_alter_statements(
    table_name: str, inferred_types: Dict[str, List[Tuple[str, int]]], force: bool = False
) -> List[str]:
    """
    Generate ALTER TABLE statements to modify column types based on the top match.
    """
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


def main():
    parser = argparse.ArgumentParser(description="Infer column types and generate ALTER TABLE statements for DuckDB.")
    parser.add_argument("--rows", type=int, default=1000, help="Number of rows to sample for type inference.")
    parser.add_argument("--force", action="store_true", help="Use TRY_CAST instead of CAST.")

    parser.add_argument("db_file", type=str, help="Path to the DuckDB file.")
    parser.add_argument("table_name", type=str, help="Name of the table to modify.")
    args = parser.parse_args()

    conn = duckdb.connect(args.db_file)

    inferred_types = infer_column_types(conn, args.table_name, args.rows)

    print("\nTop 3 inferred types for each column:")
    for col_name, matches in inferred_types.items():
        print(f"\nColumn: {col_name}")
        print(tabulate(matches, headers=["Type", "Valid Rows"], tablefmt="pretty"))

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
