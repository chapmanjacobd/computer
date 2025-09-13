#!/usr/bin/python3
import sqlite3
import concurrent.futures
import timeit
import argparse
import os


def create_database(db_path, num_rows):
    """Creates a SQLite database with a table populated with test data."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS test_data")
    cursor.execute("CREATE TABLE test_data (id INTEGER, value TEXT)")

    data = [(i, f"value_{i}") for i in range(num_rows)]
    cursor.executemany("INSERT INTO test_data VALUES (?, ?)", data)
    conn.commit()
    conn.close()


def read_data(db_path, num_rows):
    """Reads a specified number of rows from a SQLite database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM test_data LIMIT {num_rows}")
    rows = cursor.fetchall()
    conn.close()
    return len(rows)


def benchmark_read(executor_class, db_paths, num_rows):
    """Performs the database read benchmark using the specified executor."""
    with executor_class() as executor:
        futures = {executor.submit(read_data, path, num_rows): path for path in db_paths}

        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    return sum(results)


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark ThreadPoolExecutor vs. ProcessPoolExecutor for database reads."
    )
    parser.add_argument(
        "--executor",
        type=str,
        choices=["thread", "process"],
        required=True,
        help="Executor type: 'thread' or 'process'.",
    )
    parser.add_argument("--rows", type=int, default=5000, help="Number of rows to read from each database.")
    parser.add_argument("--dbs", type=int, default=2, help="Number of SQLite databases to use.")
    args = parser.parse_args()

    db_paths = [f"test_db_{i}.sqlite" for i in range(args.dbs)]

    print(f"Creating {args.dbs} databases with {args.rows} rows each...")
    for path in db_paths:
        create_database(path, args.rows)
    print("Databases created successfully.")

    executor_class = (
        concurrent.futures.ThreadPoolExecutor if args.executor == "thread" else concurrent.futures.ProcessPoolExecutor
    )

    # Use timeit to benchmark the core logic
    timer = timeit.Timer(
        stmt="benchmark_read(executor_class, db_paths, args.rows)",
        globals={
            "benchmark_read": benchmark_read,
            "executor_class": executor_class,
            "db_paths": db_paths,
            "args": args,
        },
    )

    total_time = timer.timeit(number=10)

    # Calculate total rows read (this part is outside the timer)
    total_rows = benchmark_read(executor_class, db_paths, args.rows)

    print(f"\nBenchmark results for {args.executor.capitalize()}PoolExecutor:")
    print(f"Total time to read from {args.dbs} databases: {total_time:.4f} seconds")
    print(f"Total rows read: {total_rows}")

    for path in db_paths:
        os.remove(path)


if __name__ == "__main__":
    main()
