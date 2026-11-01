
from pathlib import Path
import pandas as pd

OUTPUT = Path(r"C:\Project_03\publication\evidence")

FILES = [
    "prioritized_findings_register.csv",
    "date_field_quality_summary.csv",
    "missing_dosage_by_product_group.csv",
    "missing_insurance_by_product_group.csv",
    "pricing_discrepancy_by_product_group.csv",
    "unit_price_uom_rounding_overall.csv",
    "zero_unit_price_by_group.csv",
    "weight_freight_classification_summary.csv",
]

for filename in FILES:
    path = OUTPUT / filename

    print(f"\n{'=' * 70}")
    print(filename)
    print("=" * 70)

    df = pd.read_csv(path, encoding="utf-8-sig", nrows=2)

    print("Columns:", df.columns.tolist())
    print(df.to_string(index=False))



from pathlib import Path
import pandas as pd

OUTPUT = Path(r"C:\Project_03\publication\evidence")

# Print all findings, but keep the display focused on dashboard fields.
findings = pd.read_csv(
    OUTPUT / "prioritized_findings_register.csv",
    encoding="utf-8-sig"
)

print("\n" + "=" * 70)
print("PRIORITIZED FINDINGS REGISTER")
print("=" * 70)

columns = [
    "finding_id",
    "quality_dimension",
    "severity",
    "investigation_priority",
    "priority_status",
]

print(findings[columns].to_string(index=False))

# These are compact summary tables suitable for dashboard planning.
FILES = [
    "date_field_quality_summary.csv",
    "missing_dosage_by_product_group.csv",
    "missing_insurance_by_product_group.csv",
    "pricing_discrepancy_by_product_group.csv",
    "unit_price_uom_rounding_overall.csv",
    "zero_unit_price_by_group.csv",
    "weight_freight_classification_summary.csv",
]

for filename in FILES:
    path = OUTPUT / filename

    print(f"\n{'=' * 70}")
    print(filename)
    print("=" * 70)

    df = pd.read_csv(path, encoding="utf-8-sig")
    print("Rows:", len(df))
    print(df.to_string(index=False))
