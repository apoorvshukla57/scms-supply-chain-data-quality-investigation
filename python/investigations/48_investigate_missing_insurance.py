
from pathlib import Path
import pandas as pd

BASE = Path(r"C:\Project_03")
SOURCE = BASE / "dataset" / "Suppy_Chain_Shipment_Data.csv"
OUTPUT = BASE / "publication" / "execution" / "outputs"

INSURANCE_COL = "line item insurance (usd)"

GROUP_COLUMNS = [
    "product group",
    "sub classification",
    "shipment mode",
    "country",
    "vendor",
    "fulfill via",
    "vendor inco term",
    "managed by",
]


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(SOURCE, low_memory=False)

    if INSURANCE_COL not in df.columns:
        raise KeyError(
            f"Missing column {INSURANCE_COL!r}. "
            f"Available columns: {df.columns.tolist()}"
        )

    raw = df[INSURANCE_COL].astype("string").str.strip()
    missing = raw.isna() | raw.eq("")

    print(f"Source shape: {df.shape}")
    print(
        f"Missing insurance: {missing.sum():,}/{len(df):,} "
        f"({missing.mean() * 100:.2f}%)"
    )
    print(f"Non-missing insurance: {(~missing).sum():,}")

    audit = df.copy()
    audit["_insurance_missing"] = missing

    for col in GROUP_COLUMNS:
        if col not in df.columns:
            print(f"\nSkipping unavailable column: {col}")
            continue

        summary = (
            audit.groupby(col, dropna=False)
            .agg(
                total_records=("_insurance_missing", "size"),
                missing_insurance=("_insurance_missing", "sum"),
            )
            .reset_index()
        )

        summary["missing_percentage"] = (
            summary["missing_insurance"]
            / summary["total_records"] * 100
        )

        summary = summary.sort_values(
            ["missing_insurance", "total_records"],
            ascending=[False, False],
        )

        filename = col.replace("/", "_").replace(" ", "_")
        output_path = (
            OUTPUT / f"missing_insurance_by_{filename}.csv"
        )
        summary.to_csv(output_path, index=False)

        print(f"\n--- Missing insurance by {col} ---")
        print(summary.head(15).to_string(index=False))
        print(f"Saved: {output_path}")

    # Compare recorded line-item values without assuming missing
    # insurance means zero or an insurance-related loss.
    if "line item value" in df.columns:
        value = pd.to_numeric(df["line item value"], errors="coerce")
        audit["_line_item_value"] = value

        print("\n--- Line-item value comparison ---")
        print(
            audit.groupby("_insurance_missing")["_line_item_value"]
            .agg(["count", "median", "mean", "min", "max"])
            .to_string()
        )

    detail_cols = [
        c for c in [
            "id",
            "project code",
            "pq #",
            "po / so #",
            "asn/dn #",
            "country",
            "product group",
            "sub classification",
            "shipment mode",
            "vendor",
            "line item quantity",
            "line item value",
            INSURANCE_COL,
        ]
        if c in df.columns
    ]

    detail_path = OUTPUT / "missing_insurance_records_for_review.csv"
    df.loc[missing, detail_cols].to_csv(detail_path, index=False)

    print(f"\nAffected-record details saved: {detail_path}")
    print("Source data was not modified.")


if __name__ == "__main__":
    main()
