
from pathlib import Path
import pandas as pd

BASE_DIR = Path(r"C:\Project_03")
DATA_FILE = BASE_DIR / "dataset" / "Suppy_Chain_Shipment_Data.csv"
OUTPUT_DIR = BASE_DIR / "publication" / "execution" / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_FILE, encoding="utf-8-sig", low_memory=False)

quantity = pd.to_numeric(df["line item quantity"], errors="coerce")
pack_price = pd.to_numeric(df["pack price"], errors="coerce")
line_value = pd.to_numeric(df["line item value"], errors="coerce")

valid = (
    quantity.notna()
    & pack_price.notna()
    & line_value.notna()
    & quantity.ne(0)
)

result = pd.DataFrame({
    "id": df["id"],
    "product_group": df["product group"],
    "vendor": df["vendor"],
    "item_description": df["item description"],
    "quantity": quantity,
    "pack_price": pack_price,
    "line_value": line_value,
})

result["implied_pack_price"] = (
    result["line_value"] / result["quantity"].where(quantity.ne(0))
)

result["implied_price_rounded_2dp"] = (
    result["implied_pack_price"].round(2)
)

result["rounded_price_matches"] = (
    result["implied_price_rounded_2dp"].sub(
        result["pack_price"]
    ).abs() < 0.000001
)

result["calculated_value"] = result["quantity"] * result["pack_price"]
result["value_difference"] = result["line_value"] - result["calculated_value"]
result["absolute_difference"] = result["value_difference"].abs()

result = result.loc[valid].copy()

# Overall results
total = len(result)
matches = int(result["rounded_price_matches"].sum())
exceptions = result.loc[~result["rounded_price_matches"]].copy()

print("\nLINE-VALUE ROUNDING INVESTIGATION")
print("=" * 60)
print(f"Comparable records: {total:,}")
print(f"Implied price rounds to recorded pack price: {matches:,}")
print(f"Rounded-price mismatches: {len(exceptions):,}")
print(f"Match rate: {matches / total:.2%}" if total else "Match rate: N/A")

# Test specifically the 549 records from investigation 30.
flagged = result.loc[
    result["absolute_difference"] > 0.02
].copy()

flagged_matches = int(flagged["rounded_price_matches"].sum())

print("\nPREVIOUSLY FLAGGED RECORDS")
print("=" * 60)
print(f"Records exceeding $0.02 tolerance: {len(flagged):,}")
print(f"Explained by rounded implied price: {flagged_matches:,}")
print(
    f"Share explained: {flagged_matches / len(flagged):.2%}"
    if len(flagged) else "Share explained: N/A"
)

# Breakdown by product group
group_summary = (
    result.groupby("product_group", dropna=False)
    .agg(
        records=("id", "size"),
        rounded_price_matches=("rounded_price_matches", "sum"),
    )
    .reset_index()
)

group_summary["mismatches"] = (
    group_summary["records"] - group_summary["rounded_price_matches"]
)
group_summary["match_rate"] = (
    group_summary["rounded_price_matches"] / group_summary["records"]
)

group_summary.to_csv(
    OUTPUT_DIR / "line_value_rounding_by_group.csv",
    index=False
)

print("\nRESULTS BY PRODUCT GROUP")
print(group_summary.to_string(index=False))

# Save every record that fails the rounding test.
exceptions.sort_values(
    "absolute_difference", ascending=False
).to_csv(
    OUTPUT_DIR / "line_value_rounding_exceptions.csv",
    index=False
)

# Save a compact review of the largest previous exceptions.
flagged.sort_values(
    "absolute_difference", ascending=False
).head(20).to_csv(
    OUTPUT_DIR / "line_value_rounding_flagged_review.csv",
    index=False
)

print("\nOutputs saved to:", OUTPUT_DIR)
print("Investigation completed.")
