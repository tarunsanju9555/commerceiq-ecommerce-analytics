
from pathlib import Path
import pandas as pd

project_root = Path(__file__).resolve().parent.parent
raw_dir = project_root / "data" / "raw"

file_path = raw_dir / "olist_order_reviews_dataset.csv"
reviews = pd.read_csv(file_path)

print("=" * 60)
print("ORDER REVIEWS DATA INSPECTION")
print("=" * 60)

print("\n1. DATASET OVERVIEW")
print("Shape:", reviews.shape)
print("Columns:", reviews.columns.tolist())
print("\nData types:")
print(reviews.dtypes)

print("\n2. MISSING VALUES")
print(reviews.isnull().sum())

print("\n3. DUPLICATES")
print("Exact duplicate rows:", reviews.duplicated().sum())
print("Unique review IDs:", reviews["review_id"].nunique())
print("Duplicate review IDs:", reviews["review_id"].duplicated().sum())
print("Unique order IDs:", reviews["order_id"].nunique())
print("Duplicate order IDs:", reviews["order_id"].duplicated().sum())

print("\n4. REVIEW SCORES")
print(reviews["review_score"].value_counts().sort_index())
print("\nScore summary:")
print(reviews["review_score"].describe())

print("\n5. DATE FIELDS")
date_columns = [
    "review_creation_date",
    "review_answer_timestamp",
]

for column in date_columns:
    reviews[column] = pd.to_datetime(reviews[column], errors="coerce")
    print(
        f"{column}: missing/invalid = "
        f"{reviews[column].isna().sum()}"
    )

print("\n6. REVIEW-TO-ORDER RELATIONSHIP")
print("Review records:", len(reviews))
print("Orders with reviews:", reviews["order_id"].nunique())
print(
    "Orders with multiple review records:",
    (reviews["order_id"].value_counts() > 1).sum()
)

print("\nInspection complete.")
