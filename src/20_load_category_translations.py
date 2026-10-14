
from pathlib import Path

import pandas as pd
import pyodbc

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CSV_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "product_category_name_translation.csv"
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
    "product_category_name",
    "product_category_name_english",
]


def main():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV not found: {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)

    if list(df.columns) != COLUMNS:
        raise ValueError(f"Unexpected columns: {list(df.columns)}")

    if df.isna().any().any():
        raise ValueError("Translation file contains missing values.")

    if df["product_category_name"].duplicated().any():
        raise ValueError("Duplicate Portuguese category names found.")

    if df["product_category_name_english"].duplicated().any():
        raise ValueError("Duplicate English category names found.")

    placeholders = ", ".join("?" for _ in COLUMNS)
    column_names = ", ".join(f"[{c}]" for c in COLUMNS)

    insert_sql = (
        f"INSERT INTO dbo.CategoryTranslations ({column_names}) "
        f"VALUES ({placeholders})"
    )

    print("Translations to load:", len(df))

    with pyodbc.connect(
        CONNECTION_STRING, timeout=10
    ) as connection:
        cursor = connection.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM dbo.CategoryTranslations"
        )
        existing_rows = cursor.fetchone()[0]

        if existing_rows != 0:
            raise RuntimeError(
                f"CategoryTranslations already contains {existing_rows} "
                "rows. Check the table before rerunning."
            )

        cursor.fast_executemany = True

        try:
            cursor.executemany(
                insert_sql,
                list(df.itertuples(index=False, name=None)),
            )

            cursor.execute(
                "SELECT COUNT(*) FROM dbo.CategoryTranslations"
            )
            loaded_rows = cursor.fetchone()[0]

            if loaded_rows != len(df):
                raise RuntimeError(
                    f"Expected {len(df)} rows, found {loaded_rows}."
                )

            connection.commit()

        except Exception:
            connection.rollback()
            raise

    print("\nCATEGORY TRANSLATIONS LOAD SUCCESSFUL")
    print("CSV rows:", len(df))
    print("SQL rows:", loaded_rows)


if __name__ == "__main__":
    main()
