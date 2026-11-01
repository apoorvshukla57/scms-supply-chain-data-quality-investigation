
from pathlib import Path
import csv

# Project paths
PROJECT_DIR = Path(r"C:\Project_03")
OUTPUT_DIR = PROJECT_DIR / "publication" / "execution" / "outputs"
OUTPUT_FILE = OUTPUT_DIR / "initial_findings_register.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Findings established by the investigations completed so far.
# Classification describes the evidence, not an automatic claim of error.
findings = [
    {
        "finding_id": "DQ-01",
        "quality_dimension": "Completeness",
        "finding": "Missing dosage",
        "rule_tested": "Dosage should be populated where required by the business process.",
        "evidence": "1,736 of 10,324 records (16.82%) have missing dosage.",
        "classification": "Confirmed observation; impact not yet assessed",
        "severity": "Pending impact assessment",
        "recommended_action": "Confirm whether dosage is mandatory for every product and identify affected product groups.",
        "validation_status": "Count established; business requirement unconfirmed",
        "next_validation": "Assess dosage requirements by product type and downstream use."
    },
    {
        "finding_id": "DQ-02",
        "quality_dimension": "Validity and interpretability",
        "finding": "Date fields contain unavailable or non-date text",
        "rule_tested": "Date fields should contain parseable dates or documented exception values.",
        "evidence": "PQ first sent: 205 unavailable and 2,476 unparseable values. PO sent: 328 unavailable and 5,404 unparseable values.",
        "classification": "Confirmed observation; values are not automatically errors",
        "severity": "Pending impact assessment",
        "recommended_action": "Separate actual dates from documented process states and unavailable values.",
        "validation_status": "Counts and recurring text patterns established",
        "next_validation": "Confirm the meaning of each non-date category and document safe date handling."
    },
    {
        "finding_id": "DQ-03",
        "quality_dimension": "Consistency",
        "finding": "Pack-price formula discrepancies",
        "rule_tested": "Compare pack price with unit price multiplied by units per pack, using a $0.02 tolerance.",
        "evidence": "7,774 of 10,324 records differ by more than $0.02.",
        "classification": "Confirmed formula discrepancy; business rule unconfirmed",
        "severity": "Pending impact assessment",
        "recommended_action": "Investigate patterns by product, vendor and other relevant groups before proposing corrections.",
        "validation_status": "Discrepancy count established; formula not confirmed as a universal rule",
        "next_validation": "Confirm the pricing definitions, units and expected calculation with source documentation."
    },
    {
        "finding_id": "DQ-04",
        "quality_dimension": "Validity",
        "finding": "Zero unit prices",
        "rule_tested": "Identify records where unit price equals zero.",
        "evidence": "103 records: 71 HRDT and 32 ARV. Safety-lancet records account for 58 zero-price records.",
        "classification": "Confirmed values; validity unresolved",
        "severity": "Pending impact assessment",
        "recommended_action": "Investigate product and fulfillment patterns; do not replace zero values automatically.",
        "validation_status": "Counts and major product pattern established",
        "next_validation": "Determine whether zero represents a legitimate transaction, missing price or data error."
    },
    {
        "finding_id": "DQ-05",
        "quality_dimension": "Uniqueness",
        "finding": "Potential duplicate records",
        "rule_tested": "Compare repeated-quantity candidates across all non-ID fields.",
        "evidence": "Four exact-match patterns covering eight records match across all 32 non-ID fields.",
        "classification": "Confirmed exact matches; duplicate status unresolved",
        "severity": "Pending impact assessment",
        "recommended_action": "Retain the original records and investigate transaction-level context before any removal.",
        "validation_status": "All four patterns validated against the full dataset",
        "next_validation": "Determine whether the records represent repeated transactions or accidental duplication."
    },
    {
        "finding_id": "DQ-06",
        "quality_dimension": "Usability",
        "finding": "Weight and freight fields mix numbers and explanatory text",
        "rule_tested": "Measure numeric availability and classify non-numeric values.",
        "evidence": "Weight numeric coverage: 61.72%. Freight numeric coverage: 60.03%.",
        "classification": "Confirmed usability limitation; not all text values are errors",
        "severity": "Pending impact assessment",
        "recommended_action": "Keep the raw fields and create separately documented classifications for numeric, reference and explanatory values.",
        "validation_status": "All 10,324 records classified; no records left unclassified",
        "next_validation": "Define which analyses require numeric values and how each text category should be handled."
    },
    {
        "finding_id": "DQ-07",
        "quality_dimension": "Referential integrity",
        "finding": "Weight and freight values contain references to other records",
        "rule_tested": "Extract referenced IDs and validate target existence and shipment identifiers.",
        "evidence": "4,890 reference occurrences; all target IDs exist. All 2,445 distinct reference IDs match the tested ASN/DN, PO/SO and country fields.",
        "classification": "Reference integrity validated for tested IDs; value-transfer rules unresolved",
        "severity": "Pending impact assessment",
        "recommended_action": "Document reference semantics and prevent automatic copying or double-counting until rules are confirmed.",
        "validation_status": "Target existence and shipment-identifier matches validated",
        "next_validation": "Confirm whether references denote shipment-level values, shared values or another business convention."
    },
    {
        "finding_id": "DQ-08",
        "quality_dimension": "Completeness",
        "finding": "Missing line-item insurance values",
        "rule_tested": "Identify missing values in line-item insurance.",
        "evidence": "287 of 10,324 records (2.78%) have missing line-item insurance.",
        "classification": "Confirmed observation; impact not yet assessed",
        "severity": "Pending impact assessment",
        "recommended_action": "Determine whether insurance is required for every shipment and whether missing values mean not applicable or unknown.",
        "validation_status": "Missing-value count established; business meaning unconfirmed",
        "next_validation": "Compare missingness with shipment characteristics and applicable insurance rules."
    }
]

fieldnames = [
    "finding_id",
    "quality_dimension",
    "finding",
    "rule_tested",
    "evidence",
    "classification",
    "severity",
    "recommended_action",
    "validation_status",
    "next_validation",
]

with OUTPUT_FILE.open("w", newline="", encoding="utf-8-sig") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(findings)

# Basic output validation
with OUTPUT_FILE.open("r", newline="", encoding="utf-8-sig") as file:
    saved_rows = list(csv.DictReader(file))

assert len(saved_rows) == len(findings), "Finding count does not match."
assert len({row["finding_id"] for row in saved_rows}) == len(saved_rows), (
    "Duplicate finding IDs detected."
)
assert all(
    row["finding_id"] and row["finding"] and row["evidence"]
    for row in saved_rows
), "A required field is blank."

print("INITIAL FINDINGS REGISTER CREATED")
print(f"Findings saved: {len(saved_rows)}")
print(f"Unique finding IDs: {len({row['finding_id'] for row in saved_rows})}")
print(f"Output file: {OUTPUT_FILE}")
print("Validation: PASSED")
print("Note: Severity and business implications still require assessment.")
