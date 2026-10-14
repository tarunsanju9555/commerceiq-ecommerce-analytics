
from pathlib import Path
import pandas as pd

project_root = Path(__file__).resolve().parent.parent
raw_dir = project_root / "data" / "raw"
processed_dir = project_root / "data" / "processed"
processed_dir.mkdir(parents=True, exist_ok=True)

reviews = pd.read_csv(raw_dir / "olist_order_reviews_dataset.csv")
orders = pd.read_csv(raw_dir / "olist_orders_dataset.csv")

print("=" * 60)
print("REVIEW DATA QUALITY VALIDATION")
print("=" * 60)

# 1. Validate review scores
invalid_scores = ~reviews["review_score"].between(1, 5)
print("\n1. REVIEW SCORES")
print("Invalid scores:", invalid_scores.sum())

# 2. Validate order references
known_order_ids = set(orders["order_id"])
unknown_order_mask = ~reviews["order_id"].isin(known_order_ids)

print("\n2. ORDER REFERENCES")
print("Review records:", len(reviews))
print("Orders with reviews:", reviews["order_id"].nunique())
print("Review records with unknown orders:", unknown_order_mask.sum())
print(
    "Distinct unknown order IDs:",
    reviews.loc[unknown_order_mask, "order_id"].nunique()
)

# 3. Investigate repeated review IDs
review_id_counts = reviews["review_id"].value_counts()
duplicate_review_ids = review_id_counts[review_id_counts > 1]

print("\n3. REPEATED REVIEW IDS")
print("Repeated review IDs:", len(duplicate_review_ids))
print(
    "Rows belonging to repeated review IDs:",
    reviews["review_id"].isin(duplicate_review_ids.index).sum()
)

print("\nExamples of repeated review IDs:")
print(
    reviews[reviews["review_id"].isin(duplicate_review_ids.index)]
    .sort_values("review_id")
    .head(10)
    .to_string(index=False)
)

# 4. Inspect repeated reviews per order
order_review_counts = reviews["order_id"].value_counts()

print("\n4. MULTIPLE REVIEWS PER ORDER")
print("Orders with multiple review records:", (order_review_counts > 1).sum())
print("Maximum review records for one order:", order_review_counts.max())

# 5. Check date order
reviews["review_creation_date"] = pd.to_datetime(
    reviews["review_creation_date"], errors="coerce"
)
reviews["review_answer_timestamp"] = pd.to_datetime(
    reviews["review_answer_timestamp"], errors="coerce"
)

invalid_date_order = (
    reviews["review_answer_timestamp"]
    < reviews["review_creation_date"]
)

print("\n5. REVIEW TIMESTAMPS")
print("Invalid/missing creation dates:", reviews["review_creation_date"].isna().sum())
print("Invalid/missing answer timestamps:", reviews["review_answer_timestamp"].isna().sum())
print("Answer timestamp before creation date:", invalid_date_order.sum())

# 6. Save a validation report
report = pd.DataFrame({
    "check": [
        "total_review_records",
        "unique_review_ids",
        "repeated_review_ids",
        "orders_with_reviews",
        "unknown_order_reference_rows",
        "invalid_scores",
        "invalid_date_sequences",
    ],
    "result": [
        len(reviews),
        reviews["review_id"].nunique(),
        len(duplicate_review_ids),
        reviews["order_id"].nunique(),
        int(unknown_order_mask.sum()),
        int(invalid_scores.sum()),
        int(invalid_date_order.sum()),
    ],
})

report_path = processed_dir / "reviews_validation_report.csv"
report.to_csv(report_path, index=False)

print("\nReport saved to:", report_path)
print("\nValidation complete.")
