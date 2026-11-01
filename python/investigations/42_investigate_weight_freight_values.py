
from pathlib import Path
import pandas as pd

BASE = Path(r"C:\Project_03")
SOURCE = BASE / "dataset" / "Suppy_Chain_Shipment_Data.csv"
OUTPUT = BASE / "publication" / "execution" / "outputs"

RECORDS_OUT = OUTPUT / "weight_freight_value_classification.csv"
SUMMARY_OUT = OUTPUT / "weight_freight_classification_summary.csv"
EXAMPLES_OUT = OUTPUT / "weight_freight_nonnumeric_examples.csv"

FIELDS = ["weight (kilograms)", "freight cost (usd)"]


def classify_value(value):
    if pd.isna(value):
        return "Blank"

    text = str(value).strip()

    if text == "":
        return "Blank"

    # Numeric strings, including zero and negative values, remain numeric.
    # This script classifies values; it does not judge business validity.
    try:
        number = float(text)
        if pd.notna(number):
            return "Numeric"
    except (ValueError, TypeError):
        pass

    return "Nonnumeric text"


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(SOURCE, low_memory=False)

    if "id" not in df.columns:
        raise ValueError("Expected 'id' column not found in source.")
    if df["id"].isna().any() or df["id"].duplicated().any():
        raise ValueError("Source IDs are missing or non-unique.")

    missing_fields = set(FIELDS) - set(df.columns)
    if missing_fields:
        raise ValueError(f"Missing expected fields: {sorted(missing_fields)}")

    evidence = df[["id"] + FIELDS].copy()

    summary_rows = []
    example_frames = []

    for field in FIELDS:
        status_col = f"{field} - classification"
        evidence[status_col] = df[field].map(classify_value)

        counts = evidence[status_col].value_counts()

        for category in ["Numeric", "Blank", "Nonnumeric text"]:
            count = int(counts.get(category, 0))
            summary_rows.append({
                "field": field,
                "classification": category,
                "record_count": count,
                "percentage_of_dataset": round(
                    count / len(df) * 100, 2
                ) if len(df) else 0,
            })

        # Preserve all original values for nonnumeric examples.
        examples = evidence.loc[
            evidence[status_col].eq("Nonnumeric text"),
            ["id", field, status_col]
        ].copy()

        examples.insert(0, "field", field)
        example_frames.append(examples)

    summary = pd.DataFrame(summary_rows)
    examples_all = pd.concat(example_frames, ignore_index=True)

    evidence.to_csv(RECORDS_OUT, index=False)
    summary.to_csv(SUMMARY_OUT, index=False)
    examples_all.to_csv(EXAMPLES_OUT, index=False)

    print(f"Source records: {len(df):,}")
    print(f"Fields classified: {len(FIELDS)}")

    print("\nClassification summary:")
    print(summary.to_string(index=False))

    print("\nMost frequent nonnumeric values by field:")
    for field in FIELDS:
        status_col = f"{field} - classification"
        mask = evidence[status_col].eq("Nonnumeric text")
        counts = (
            evidence.loc[mask, field]
            .astype(str)
            .value_counts()
            .head(15)
        )

        print(f"\n{field}:")
        if counts.empty:
            print("No nonnumeric text found.")
        else:
            print(counts.to_string())

    print("\nOutput files:")
    print(RECORDS_OUT)
    print(SUMMARY_OUT)
    print(EXAMPLES_OUT)
    print("\nOriginal source data was not modified.")


if __name__ == "__main__":
    main()
