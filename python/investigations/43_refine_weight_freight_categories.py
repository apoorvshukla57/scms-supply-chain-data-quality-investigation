
from pathlib import Path
import re
import math
import pandas as pd

PROJECT_BASE = Path(r"C:\Project_03")
PUBLICATION_BASE = PROJECT_BASE / "publication"

SOURCE = PROJECT_BASE / "dataset" / "Suppy_Chain_Shipment_Data.csv"
OUTPUT = PUBLICATION_BASE / "execution" / "outputs"

SUMMARY_OUT = OUTPUT / "weight_freight_refined_categories.csv"
EXAMPLES_OUT = OUTPUT / "weight_freight_reference_examples.csv"

FIELDS = ["weight (kilograms)", "freight cost (usd)"]

REFERENCE_PATTERN = re.compile(
    r"\bSee\s+(?:DN|ASN)\b.*\bID\s*#?\s*:\s*\d+",
    flags=re.IGNORECASE,
)


def classify(value):
    if pd.isna(value) or str(value).strip() == "":
        return "Blank"

    text = str(value).strip()

    try:
        number = float(text)
        if math.isfinite(number):
            return "Numeric"
    except (ValueError, TypeError):
        pass

    if REFERENCE_PATTERN.search(text):
        return "Cross-record reference"

    return "Other explanatory or nonnumeric text"


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(SOURCE, low_memory=False)

    if "id" not in df.columns or df["id"].isna().any():
        raise ValueError("Source ID validation failed.")

    rows = []
    reference_examples = []

    for field in FIELDS:
        categories = df[field].map(classify)

        for category, count in categories.value_counts().items():
            rows.append({
                "field": field,
                "category": category,
                "record_count": int(count),
                "percentage_of_dataset": round(
                    int(count) / len(df) * 100, 2
                ),
            })

        mask = categories.eq("Cross-record reference")

        for _, record in df.loc[mask, ["id", field]].iterrows():
            match = REFERENCE_PATTERN.search(str(record[field]))

            reference_id_match = re.search(
                r"ID\s*#?\s*:\s*(\d+)",
                str(record[field]),
                flags=re.IGNORECASE,
            )

            reference_examples.append({
                "source_id": record["id"],
                "field": field,
                "original_value": record[field],
                "referenced_document": (
                    match.group(0).split("(")[0].strip()
                    if match else None
                ),
                "reference_id": (
                    reference_id_match.group(1)
                    if reference_id_match else None
                ),
            })

    summary = pd.DataFrame(rows).sort_values(
        ["field", "category"]
    )

    examples = pd.DataFrame(reference_examples)

    summary.to_csv(SUMMARY_OUT, index=False)
    examples.to_csv(EXAMPLES_OUT, index=False)

    print("Refined category summary:")
    print(summary.to_string(index=False))

    print(f"\nCross-record reference occurrences: {len(examples)}")

    print(
        "\nUnique source records with references: "
        f"{examples['source_id'].nunique() if not examples.empty else 0}"
    )

    print(f"\nSummary output: {SUMMARY_OUT}")
    print(f"Reference examples: {EXAMPLES_OUT}")
    print("\nSource data was not modified.")


if __name__ == "__main__":
    main()

