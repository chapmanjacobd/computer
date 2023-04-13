#!/usr/bin/python

import argparse
import pickle
import pandas as pd

from eda import eda

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
    eda(df)
