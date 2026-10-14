
from pathlib import Path

import pandas as pd
import pyodbc

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = (
    PROJECT_ROOT / "data" / "raw" / "olist_customers_dataset.csv"
)

CONNECTION_STRING = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    r"SERVER=TARUN\SQLEXPRESS;"
    "DATABASE=CustomerSalesIntelligence;"
    "Trusted_Connection=yes;"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)

COLUMNS = [
    "customer_id",
    "customer_unique_id",
    "customer_zip_code_prefix",
    "customer_city",
    "customer_state",
]


def main():
    if not CSV_PATH.exists():
        raise FileNotFoundError(CSV_PATH)

    df = pd.read_csv(CSV_PATH)

    if list(df.columns) != COLUMNS:
        raise ValueError(f"Unexpected columns: {df.columns.tolist()}")

    if df.isna().any().any():
        raise ValueError("Missing customer values found.")

    if df["customer_id"].duplicated().any():
        raise ValueError("Duplicate customer IDs found.")

    print("Rows to load:", len(df))
    print("Unique customer IDs:", df["customer_id"].nunique())
    print("Unique underlying customers:",
          df["customer_unique_id"].nunique())

    with pyodbc.connect(CONNECTION_STRING, timeout=10) as connection:
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM dbo.Customers")
        existing_rows = cursor.fetchone()[0]

        if existing_rows != 0:
            raise RuntimeError(
                f"dbo.Customers already has {existing_rows} rows. "
                "Nothing was inserted."
            )

        placeholders = ", ".join("?" for _ in COLUMNS)
        column_names = ", ".join(f"[{c}]" for c in COLUMNS)

        insert_sql = (
            f"INSERT INTO dbo.Customers ({column_names}) "
            f"VALUES ({placeholders})"
        )

        cursor.fast_executemany = True

        try:
            cursor.executemany(
                insert_sql,
                list(df.itertuples(index=False, name=None)),
            )

            cursor.execute("SELECT COUNT(*) FROM dbo.Customers")
            loaded_rows = cursor.fetchone()[0]

            if loaded_rows != len(df):
                raise RuntimeError(
                    f"Expected {len(df)} rows, found {loaded_rows}."
                )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

    print("\nCUSTOMERS LOAD SUCCESSFUL")
    print("CSV rows:", len(df))
    print("SQL rows:", loaded_rows)


if __name__ == "__main__":
    main()
