
from pathlib import Path

import pandas as pd
import pyodbc

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CSV_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "olist_order_payments_dataset.csv"
)

SERVER = r"TARUN\SQLEXPRESS"
DATABASE = "CustomerSalesIntelligence"
DRIVER = "ODBC Driver 18 for SQL Server"

CONNECTION_STRING = (
    f"DRIVER={{{DRIVER}}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    "Trusted_Connection=yes;"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)

COLUMNS = [
    "order_id",
    "payment_sequential",
    "payment_type",
    "payment_installments",
    "payment_value",
]


def main():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV not found: {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)

    if list(df.columns) != COLUMNS:
        raise ValueError(f"Unexpected CSV columns: {list(df.columns)}")

    if df.isna().any().any():
        raise ValueError("CSV contains missing values.")

    if df.duplicated(
        subset=["order_id", "payment_sequential"]
    ).any():
        raise ValueError("Duplicate order-payment keys found.")

    if (df["payment_installments"] < 0).any():
        raise ValueError("Negative installment values found.")

    if (df["payment_value"] < 0).any():
        raise ValueError("Negative payment values found.")

    placeholders = ", ".join("?" for _ in COLUMNS)
    column_names = ", ".join(f"[{c}]" for c in COLUMNS)

    insert_sql = (
        f"INSERT INTO dbo.Payments ({column_names}) "
        f"VALUES ({placeholders})"
    )

    print("Rows to load:", len(df))
    print("Unique order-payment keys:", len(df))

    with pyodbc.connect(
        CONNECTION_STRING, timeout=10
    ) as connection:
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM dbo.Payments")
        existing_rows = cursor.fetchone()[0]

        if existing_rows != 0:
            raise RuntimeError(
                f"dbo.Payments already contains {existing_rows} rows. "
                "No data was inserted. Check the table before rerunning."
            )

        cursor.fast_executemany = True

        try:
            cursor.executemany(
                insert_sql,
                list(df.itertuples(index=False, name=None)),
            )

            cursor.execute("SELECT COUNT(*) FROM dbo.Payments")
            loaded_rows = cursor.fetchone()[0]

            if loaded_rows != len(df):
                raise RuntimeError(
                    f"Expected {len(df)} rows but found {loaded_rows}."
                )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

    print("\nPAYMENTS LOAD SUCCESSFUL")
    print("CSV rows:", len(df))
    print("SQL rows:", loaded_rows)
    print("Orders with payments:", df["order_id"].nunique())


if __name__ == "__main__":
    main()
