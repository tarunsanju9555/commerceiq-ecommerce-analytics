
from pathlib import Path

import pandas as pd
import pyodbc


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"

CSV_PATH = RAW_DIR / "olist_sellers_dataset.csv"

CONNECTION_STRING = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    r"SERVER=TARUN\SQLEXPRESS;"
    "DATABASE=CustomerSalesIntelligence;"
    "Trusted_Connection=yes;"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)


def main():
    sellers = pd.read_csv(CSV_PATH)

    # Confirm source-data integrity before loading.
    required_columns = [
        "seller_id",
        "seller_zip_code_prefix",
        "seller_city",
        "seller_state",
    ]

    if sellers[required_columns].isnull().any().any():
        raise ValueError("Missing values found in required seller columns.")

    if sellers["seller_id"].duplicated().any():
        raise ValueError("Duplicate seller IDs found.")

    with pyodbc.connect(CONNECTION_STRING) as conn:
        cursor = conn.cursor()

        existing_count = cursor.execute(
            "SELECT COUNT(*) FROM dbo.Sellers"
        ).fetchone()[0]

        if existing_count > 0:
            raise RuntimeError(
                f"dbo.Sellers already contains {existing_count} rows. "
                "Stopping to prevent duplicate loading."
            )

        insert_sql = """
            INSERT INTO dbo.Sellers (
                seller_id,
                seller_zip_code_prefix,
                seller_city,
                seller_state
            )
            VALUES (?, ?, ?, ?)
        """

        records = list(
            sellers[required_columns].itertuples(
                index=False, name=None
            )
        )

        cursor.fast_executemany = True
        cursor.executemany(insert_sql, records)
        conn.commit()

        sql_count = cursor.execute(
            "SELECT COUNT(*) FROM dbo.Sellers"
        ).fetchone()[0]

        print("=" * 50)
        print("SELLER SQL LOAD RESULTS")
        print("=" * 50)
        print("Source records:", len(sellers))
        print("SQL records:", sql_count)
        print("Unique source seller IDs:", sellers["seller_id"].nunique())

        if sql_count != len(sellers):
            raise RuntimeError("SQL row count does not match source count.")

        print("\nSeller data loaded and verified successfully!")


if __name__ == "__main__":
    main()
