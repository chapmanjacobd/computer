#!/usr/bin/python3
import sqlite3
import duckdb
import time
import random
import string
import os
import pandas as pd  # Import Pandas

# Benchmark parameters
NUM_INITIAL_ROWS = 2_000_000
NUM_INSERT_ROWS = 30  # Number of rows to insert for benchmark
TEXT_COLUMN_LENGTH = 100
BLOB_COLUMN_LENGTH = 200
NUM_BENCHMARK_RUNS = 300 # Run benchmark multiple times and average
DUCKDB_THREADS = 4 # Set threads for DuckDB

# Database and table names
SQLITE_DB_FILE = 'sqlite_benchmark.db'
DUCKDB_DB_FILE = 'duckdb_benchmark.db'
TABLE_NAME = 'my_table'

def generate_random_data_pandas(num_rows):
    """Generates random data for integer, text, and blob columns as Pandas Series (corrected integer generation)."""
    integer_col = pd.Series([random.randint(1_000_000, 2_000_000) for _ in range(num_rows)], dtype='int32') # Generate random integers, duplicates possible
    text_col = pd.Series([''.join(random.choices(string.ascii_letters + string.digits, k=TEXT_COLUMN_LENGTH)) for _ in range(num_rows)], dtype='string') # Use pandas 'string' dtype
    blob_col = pd.Series([os.urandom(BLOB_COLUMN_LENGTH) for _ in range(num_rows)], dtype='object') # Keep object dtype for blobs

    return pd.DataFrame({'integer_col': integer_col, 'text_col': text_col, 'blob_col': blob_col}) # Return DataFrame

def create_and_populate_sqlite(db_file, num_rows):
    """Creates SQLite database, table, populates initial rows and adds indexes with WAL and PRAGMAs."""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Enable WAL mode and set PRAGMAs for SQLite
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA threads = 4")
    cursor.execute("PRAGMA main.cache_size = 8000")

    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            integer_col INTEGER,
            text_col TEXT,
            blob_col BLOB
        )
    ''')

    df = generate_random_data_pandas(num_rows) # Generate pandas DataFrame
    data_tuples = list(df.itertuples(index=False)) # Convert DataFrame rows to tuples for executemany
    cursor.executemany(f"INSERT INTO {TABLE_NAME} (integer_col, text_col, blob_col) VALUES (?, ?, ?)", data_tuples)


    cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_integer ON {TABLE_NAME} (integer_col)")
    cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_text ON {TABLE_NAME} (text_col)")

    conn.commit()
    conn.close()

def create_and_populate_duckdb(db_file, num_rows):
    """Creates DuckDB database, table, populates initial rows using Pandas DataFrames."""
    conn = duckdb.connect(database=db_file, config={'threads': DUCKDB_THREADS})
    cursor = conn.cursor()

    df = generate_random_data_pandas(num_rows) # Generate pandas DataFrame

    # Create table directly from Pandas DataFrame
    conn.execute(f"CREATE TABLE IF NOT EXISTS {TABLE_NAME} AS SELECT * FROM df")

    cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_integer ON {TABLE_NAME} (integer_col)")
    cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_text ON {TABLE_NAME} (text_col)")

    conn.commit()
    conn.close()


def benchmark_sqlite_insert(db_file, num_rows_to_insert):
    """Benchmarks SQLite insert performance with WAL and PRAGMAs."""
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Enable WAL mode and set PRAGMAs for SQLite - important to do this for the benchmark connection too for fair comparison
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA threads = 4")
    cursor.execute("PRAGMA main.cache_size = 8000")

    df_insert = generate_random_data_pandas(num_rows_to_insert) # Generate pandas DataFrame for insert
    data_tuples = list(df_insert.itertuples(index=False)) # Convert DataFrame rows to tuples

    start_time = time.time()
    for r in data_tuples:
        cursor.execute(f"INSERT INTO {TABLE_NAME} (integer_col, text_col, blob_col) VALUES (?, ?, ?)", r)
    conn.commit()
    end_time = time.time()

    conn.close()
    return end_time - start_time

def benchmark_duckdb_insert(db_file, num_rows_to_insert):
    """Benchmarks DuckDB insert performance with threads set and uses executemany for insert benchmark."""
    conn = duckdb.connect(database=db_file, config={'threads': DUCKDB_THREADS})
    cursor = conn.cursor()

    df_insert_benchmark = generate_random_data_pandas(num_rows_to_insert) # Generate pandas DataFrame for benchmark insert
    data_tuples = list(df_insert_benchmark.itertuples(index=False))

    start_time = time.time()
    # 69x slower
    # cursor.executemany(f"INSERT INTO {TABLE_NAME} (integer_col, text_col, blob_col) VALUES (?, ?, ?)", data_tuples)
    # conn.commit()

    # 24x slower
    for r in data_tuples:
        cursor.execute(f"INSERT INTO {TABLE_NAME} (integer_col, text_col, blob_col) VALUES (?, ?, ?)", r)
    conn.commit()
    end_time = time.time()

    conn.close()
    return end_time - start_time

def cleanup_databases():
    """Removes database files."""
    for db_file in [SQLITE_DB_FILE, DUCKDB_DB_FILE]:
        try:
            os.remove(db_file)
        except FileNotFoundError:
            pass

if __name__ == "__main__":
    print("Setting up databases with initial data...")
    cleanup_databases() # Start fresh

    create_and_populate_sqlite(SQLITE_DB_FILE, NUM_INITIAL_ROWS)
    create_and_populate_duckdb(DUCKDB_DB_FILE, NUM_INITIAL_ROWS)
    print(f"Databases populated with {NUM_INITIAL_ROWS:,} rows each.")

    sqlite_times = []
    duckdb_times = []

    print(f"\nRunning benchmark {NUM_BENCHMARK_RUNS} times, inserting {NUM_INSERT_ROWS:,} rows each time...")
    for i in range(NUM_BENCHMARK_RUNS):
        print(f"Benchmark run {i+1}/{NUM_BENCHMARK_RUNS}:")

        sqlite_time = benchmark_sqlite_insert(SQLITE_DB_FILE, NUM_INSERT_ROWS)
        sqlite_times.append(sqlite_time)
        print(f"  SQLite Insert Time: {sqlite_time:.4f} seconds")

        duckdb_time = benchmark_duckdb_insert(DUCKDB_DB_FILE, NUM_INSERT_ROWS)
        duckdb_times.append(duckdb_time)
        print(f"  DuckDB Insert Time: {duckdb_time:.4f} seconds")

    avg_sqlite_time = sum(sqlite_times) / NUM_BENCHMARK_RUNS
    avg_duckdb_time = sum(duckdb_times) / NUM_BENCHMARK_RUNS

    print(f"\n--- Benchmark Results ---")
    print(f"Average SQLite Insert Time ({NUM_BENCHMARK_RUNS} runs): {avg_sqlite_time:.4f} seconds")
    print(f"Average DuckDB Insert Time ({NUM_BENCHMARK_RUNS} runs): {avg_duckdb_time:.4f} seconds")

    if avg_duckdb_time < avg_sqlite_time:
        speedup = avg_sqlite_time / avg_duckdb_time
        print(f"\nDuckDB is approximately {speedup:.2f} times faster than SQLite for these inserts.")
    elif avg_sqlite_time < avg_duckdb_time:
        speedup = avg_duckdb_time / avg_sqlite_time
        print(f"\nSQLite is approximately {speedup:.2f} times faster than DuckDB for these inserts.")
    else:
        print("\nSQLite and DuckDB have approximately the same insertion performance.")

    print("\nCleanup: Removing database files...")
    cleanup_databases()
    print("Benchmark finished.")
