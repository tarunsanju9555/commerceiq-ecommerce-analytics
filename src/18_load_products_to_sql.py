
from pathlib import Path

import pandas as pd
import pyodbc

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = (
    PROJECT_ROOT / "data" / "raw" / "olist_products_dataset.csv"
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
    "product_id",
    "product_category_name",
    "product_name_lenght",
    "product_description_lenght",
    "product_photos_qty",
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm",
]


def main():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV not found: {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)

    if list(df.columns) != COLUMNS:
        raise ValueError(f"Unexpected columns: {list(df.columns)}")

    if df["product_id"].isna().any():
        raise ValueError("Missing product IDs found.")

    if df["product_id"].duplicated().any():
        raise ValueError("Duplicate product IDs found.")

    # Convert pandas missing values to Python None for SQL NULL.
    df = df.astype(object).where(pd.notna(df), None)

    placeholders = ", ".join("?" for _ in COLUMNS)
    column_names = ", ".join(f"[{c}]" for c in COLUMNS)

    insert_sql = (
        f"INSERT INTO dbo.Products ({column_names}) "
        f"VALUES ({placeholders})"
    )

    print("Rows to load:", len(df))
    print("Unique product IDs:", df["product_id"].nunique())

    with pyodbc.connect(
        CONNECTION_STRING, timeout=10
    ) as connection:
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM dbo.Products")
        existing_rows = cursor.fetchone()[0]

        if existing_rows != 0:
            raise RuntimeError(
                f"dbo.Products already contains {existing_rows} rows. "
                "Nothing was inserted; inspect the table before retrying."
            )

        cursor.fast_executemany = True

        try:
            cursor.executemany(
                insert_sql,
                list(df.itertuples(index=False, name=None)),
            )

            cursor.execute("SELECT COUNT(*) FROM dbo.Products")
            loaded_rows = cursor.fetchone()[0]

            if loaded_rows != len(df):
                raise RuntimeError(
                    f"Expected {len(df)} rows, found {loaded_rows}."
                )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

    print("\nPRODUCTS LOAD SUCCESSFUL")
    print("CSV rows:", len(df))
    print("SQL rows:", loaded_rows)
    print(
        "Products with missing categories:",
        df["product_category_name"].isna().sum(),
    )


if __name__ == "__main__":
    main()
