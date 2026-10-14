
from pathlib import Path

import pandas as pd
import pyodbc

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = PROJECT_ROOT / "data" / "processed" / "orders_validated.csv"

# SQL Server settings
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

DATE_COLUMNS = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]

QUALITY_FLAGS = [
    "quality_flag_missing_delivery_date",
    "quality_flag_missing_carrier_date",
    "quality_flag_invalid_date_order",
]

VALIDATION_FLAGS = [
    "flag_carrier_before_approval",
    "flag_delivery_before_carrier",
    "flag_delivered_missing_delivery_date",
]

COLUMNS = [
    "order_id",
    "customer_id",
    "order_status",
    *DATE_COLUMNS,
    *QUALITY_FLAGS,
    *VALIDATION_FLAGS,
]


def main():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV not found: {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)

    # Check the source schema before touching SQL Server.
    if list(df.columns) != COLUMNS:
        raise ValueError(
            "CSV columns do not match the expected schema.\n"
            f"Expected: {COLUMNS}\n"
            f"Received: {list(df.columns)}"
        )

    if df["order_id"].isna().any():
        raise ValueError("order_id contains missing values.")

    if df["order_id"].duplicated().any():
        raise ValueError("Duplicate order IDs found in CSV.")

    # Convert empty date values to SQL NULL.
    for column in DATE_COLUMNS:
        df[column] = pd.to_datetime(
            df[column], errors="raise"
        )
        df[column] = df[column].astype(object).where(
            df[column].notna(), None
        )

    # Convert Boolean values to integers for SQL Server BIT.
    for column in QUALITY_FLAGS + VALIDATION_FLAGS:
        df[column] = df[column].astype(bool).astype(int)

    # Convert remaining pandas missing values to Python None.
    df = df.astype(object).where(pd.notna(df), None)

    placeholders = ", ".join("?" for _ in COLUMNS)
    column_names = ", ".join(f"[{c}]" for c in COLUMNS)

    insert_sql = (
        f"INSERT INTO dbo.Orders ({column_names}) "
        f"VALUES ({placeholders})"
    )

    print("Rows to load:", len(df))
    print("Unique order IDs:", df["order_id"].nunique())
    print("Connecting to SQL Server...")

    with pyodbc.connect(CONNECTION_STRING, timeout=10) as connection:
        cursor = connection.cursor()

        # Do not accidentally append duplicates on a rerun.
        cursor.execute("SELECT COUNT(*) FROM dbo.Orders")
        existing_rows = cursor.fetchone()[0]

        if existing_rows != 0:
            raise RuntimeError(
                f"dbo.Orders already contains {existing_rows} rows. "
                "No rows were inserted. Check the table before rerunning."
            )

        cursor.fast_executemany = True

        try:
            cursor.executemany(
                insert_sql,
                list(df.itertuples(index=False, name=None)),
            )

            cursor.execute("SELECT COUNT(*) FROM dbo.Orders")
            loaded_rows = cursor.fetchone()[0]

            if loaded_rows != len(df):
                raise RuntimeError(
                    f"Row-count mismatch: expected {len(df)}, "
                    f"found {loaded_rows}."
                )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

    print("\nLOAD SUCCESSFUL")
    print("Rows in CSV:", len(df))
    print("Rows in SQL Server:", loaded_rows)
    print("Unique order IDs:", df["order_id"].nunique())


if __name__ == "__main__":
    main()
