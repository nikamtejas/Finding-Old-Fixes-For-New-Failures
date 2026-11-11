"""Step 1: load the issue table, check it, fix the column types, save as Parquet."""
from pathlib import Path

import pandas as pd

INPUT_CSV = Path("data/processed/matter_issues_full.csv")
OUTPUT_PARQUET = Path("data/processed/issues_loaded.parquet")
EXPECTED_ROWS = 14698  # number of issues GitHub reported on the download day


def load_csv(path):
    # keep_default_na=False: an empty text stays "" and the word "NA" in an issue stays text
    return pd.read_csv(path, keep_default_na=False, encoding="utf-8-sig")


def count_empty(df):
    # With keep_default_na=False, "missing" shows up as an empty string
    empty = {}
    for column in df.columns:
        empty[column] = int((df[column].astype(str) == "").sum())
    return pd.Series(empty, name="empty_values")


def fix_types(df):
    df = df.copy()
    # Dates: text -> real timestamps (UTC), so we can sort and split by time later
    df["created_at"] = pd.to_datetime(df["created_at"], utc=True)
    df["closed_at"] = pd.to_datetime(df["closed_at"].replace("", None), utc=True)
    # Numbers: empty days_to_close (open issues) becomes NaN instead of ""
    df["days_to_close"] = pd.to_numeric(df["days_to_close"].replace("", None))
    # state_reason is empty for open issues; mark it as truly missing
    df["state_reason"] = df["state_reason"].replace("", None)
    return df


def check_table(df):
    assert len(df) == EXPECTED_ROWS, f"expected {EXPECTED_ROWS} rows, got {len(df)}"
    assert df["number"].is_unique, "issue numbers must be unique"
    # Open issues should have no close date, closed issues should have one
    is_closed = df["state"] == "closed"
    assert df.loc[is_closed, "closed_at"].notna().all()
    assert df.loc[~is_closed, "closed_at"].isna().all()
    # days_to_close should agree with the two dates (allow rounding)
    recomputed = (df["closed_at"] - df["created_at"]).dt.total_seconds() / 86400
    difference = (recomputed - df["days_to_close"]).abs()
    assert (difference[is_closed] < 0.01).all(), "days_to_close does not match the dates"
    print("All checks passed.")


def main():
    df = load_csv(INPUT_CSV)
    print(f"Rows: {len(df):,}   Columns: {df.shape[1]}")
    print("\nEmpty values per column (before type fixes):")
    print(count_empty(df).to_string())

    df = fix_types(df)
    print("\nColumn types after fixing:")
    print(df.dtypes.to_string())
    print("\nMissing values after fixing (only the expected columns should have any):")
    missing = df.isna().sum()
    print(missing[missing > 0].to_string())

    check_table(df)
    print(f"\nState: {df['state'].value_counts().to_dict()}")
    print(f"Created from {df['created_at'].min():%Y-%m-%d} to {df['created_at'].max():%Y-%m-%d}")

    df.to_parquet(OUTPUT_PARQUET, index=False)
    print(f"\nSaved {OUTPUT_PARQUET} ({OUTPUT_PARQUET.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
