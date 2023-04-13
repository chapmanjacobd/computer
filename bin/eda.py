#!/usr/bin/python

import argparse

import magic
import pandas as pd


def read_file_to_dataframe(file_path, table_index=0, nrows=None, skiprows=None):
    mime = magic.detect_from_filename(file_path)
    print(mime)

    if mime.mime_type == "text/csv":
        df = pd.read_csv(file_path, nrows=nrows, skiprows=skiprows or 0)
    elif mime.mime_type == "text/tab-separated-values":
        df = pd.read_csv(file_path, delimiter="\t", nrows=nrows, skiprows=skiprows or 0)
    elif mime.mime_type == "application/vnd.ms-excel":
        df = pd.read_excel(file_path, sheet_name=table_index, nrows=nrows, skiprows=skiprows)
    elif mime.mime_type == "application/json":
        df = pd.read_json(file_path, nrows=nrows)
    elif mime.name == 'Apache Parquet' or mime.mime_type == "application/parquet":
        df = pd.read_parquet(file_path)
    elif mime.mime_type == "application/octet-stream":
        df = pd.read_pickle(file_path)
    elif mime.mime_type == "text/html":
        dfs = pd.read_html(file_path, skiprows=skiprows)
        df = dfs[table_index]
        if nrows is not None:
            df = df.head(nrows)
    else:
        raise ValueError(f"{file_path}: Unsupported file type: {mime}")

    return df


def print_md(df):
    print(df.to_markdown(tablefmt="github"))


def print_series(s):
    if len(s) > 0:
        print()
        print("\n".join([f"- {col}" for col in s]))
        print()


def eda(df):
    print("### Shape")
    print(df.shape)
    print()
    print("### Columns")
    print_md(df.dtypes)
    print()
    print("### Converted columns")
    print_md(df.convert_dtypes().dtypes)
    print()
    print("### Sample of rows")
    print_md(df.head())
    print()
    print("### Summary statistics")
    print_md(df.describe())
    print()

    print('### NaNs')
    nan_col_sums = df.isna().sum()
    print(f'{nan_col_sums.sum():,} NaNs', f'({(nan_col_sums.sum() / (df.shape[0] * df.shape[1])):.1%})')
    print()

    no_nas = df.columns[df.notnull().all()]
    print(f"#### {len(no_nas)} columns with no NaNs")
    print_series(no_nas)

    all_nas = df.columns[df.isnull().all()]
    print(f"#### {len(all_nas)} columns with all NaNs")
    print_series(all_nas)

    print(f"#### Percent of NaNs by column")
    print_md((df.isna().mean().round(3) * 100).rename('% missing'))
    print()


def main():
    parser = argparse.ArgumentParser(description="Perform EDA on one or more files")
    parser.add_argument(
        "file_paths",
        metavar="file_path",
        nargs="+",
        help="path to one or more files",
    )
    parser.add_argument(
        "--table",
        "-t",
        type=int,
        default=0,
    )
    parser.add_argument("--start-row", "--skiprows", type=int, default=None)
    parser.add_argument("--end-row", "--nrows", type=int, default=None)
    args = parser.parse_args()
    for file_path in args.file_paths:
        print('##', file_path)
        df = read_file_to_dataframe(
            file_path,
            table_index=args.table,
            nrows=args.end_row,
            skiprows=args.start_row,
        )
        eda(df)


if __name__ == '__main__':
    main()
