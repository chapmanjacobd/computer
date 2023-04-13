#!/usr/bin/python

import argparse
import pandas as pd

parser = argparse.ArgumentParser(description="Perform EDA on one or more parquet files")
parser.add_argument(
    "file_paths",
    metavar="file_path",
    type=str,
    nargs="+",
    help="path to one or more parquet files",
)

args = parser.parse_args()
for file_path in args.file_paths:
    df = pd.read_parquet(file_path)

    print('##', file_path)
    print("### Shape")
    print(df.shape)
    print()
    print("### Columns")
    print(df.dtypes.to_markdown(tablefmt="github"))
    print()
    print("### Converted columns")
    print(df.convert_dtypes().dtypes.to_markdown(tablefmt="github"))
    print()
    print("### Sample of rows")
    print(df.head().to_markdown(tablefmt="github"))
    print()
    print("### Summary statistics")
    print(df.describe().to_markdown(tablefmt="github"))
    print()
