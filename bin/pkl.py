#!/usr/bin/python

import argparse
import pickle
import pandas as pd

parser = argparse.ArgumentParser(description="Perform EDA on one or more pickle files")
parser.add_argument(
    "file_paths",
    metavar="file_path",
    type=str,
    nargs="+",
    help="path to one or more pickle files",
)

args = parser.parse_args()
for file_path in args.file_paths:
    with open(file_path, "rb") as f:
        data = pickle.load(f)
    df = pd.DataFrame.from_dict(data)

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
