#!/usr/bin/python

import argparse
import pandas as pd

from eda import eda

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
    eda(df)
