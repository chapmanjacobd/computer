
def print_md(df):
    print(df.to_markdown(tablefmt="github"))


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

def print_series(s):
    if len(s) > 0:
        print()
        print("\n".join([f"- {col}" for col in s]))
        print()
