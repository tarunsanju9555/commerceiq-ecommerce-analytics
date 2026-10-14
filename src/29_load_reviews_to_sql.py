
from pathlib import Path
import pandas as pd
import pyodbc

root = Path(__file__).resolve().parent.parent
file = root / "data" / "raw" / "olist_order_reviews_dataset.csv"

df = pd.read_csv(file)
df["review_creation_date"] = pd.to_datetime(df["review_creation_date"])
df["review_answer_timestamp"] = pd.to_datetime(df["review_answer_timestamp"])

df = df.astype(object).where(pd.notna(df), None)

connection_string = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    r"SERVER=TARUN\SQLEXPRESS;"
    "DATABASE=CustomerSalesIntelligence;"
    "Trusted_Connection=yes;"
    "Encrypt=yes;"
    "TrustServerCertificate=yes;"
)

sql = """
INSERT INTO dbo.Reviews (
    review_id, order_id, review_score,
    review_comment_title, review_comment_message,
    review_creation_date, review_answer_timestamp
)
VALUES (?, ?, ?, ?, ?, ?, ?)
"""

with pyodbc.connect(connection_string) as conn:
    cursor = conn.cursor()

    count = cursor.execute(
        "SELECT COUNT(*) FROM dbo.Reviews"
    ).fetchone()[0]

    if count:
        raise RuntimeError(
            f"dbo.Reviews already contains {count} rows. "
            "Stopping to avoid duplicate loading."
        )

    cursor.fast_executemany = True
    cursor.executemany(sql, list(df.itertuples(index=False, name=None)))
    conn.commit()

    loaded = cursor.execute(
        "SELECT COUNT(*) FROM dbo.Reviews"
    ).fetchone()[0]

    print("Source records:", len(df))
    print("SQL records:", loaded)
    print("Reviews loaded successfully!" if loaded == len(df) else "Count mismatch!")
