
from pathlib import Path
import pandas as pd

BASE_DIR = Path(r"C:\Project_03")
OUTPUT_DIR = BASE_DIR / "publication" / "execution" / "outputs"

REGISTER_FILES = [
    OUTPUT_DIR / "initial_findings_register.csv",
    OUTPUT_DIR / "prioritized_findings_register.csv",
]

UPDATES = {
    "DQ-06": {
        "evidence": (
            "Weight: 6,372 numeric (61.72%), 2,445 cross-record references "
            "(23.68%), 1,507 other explanatory text (14.60%), and 0 blank. "
            "Freight: 6,198 numeric (60.03%), 2,445 cross-record references "
            "(23.68%), 1,681 other explanatory text (16.28%), and 0 blank. "
            "All 2,445 references in each field resolve to existing target "
            "records, and both fields reference the same target within each "
            "source record. Target ASN/DN document numbers match the extracted "
            "reference numbers in all 2,445 cases per field. No mismatches "
            "were found in the tested country, shipment mode, vendor, "
            "fulfilment method, product group, or delivered date fields. "
            "Seven references per field have different scheduled dates from "
            "their targets, although delivered dates match. Those seven "
            "pairs also differ in item description and quantity. Reference "
            "semantics and value-transfer rules remain unverified."
        ),
        "validation_status": (
            "Field classifications and tested reference links validated; "
            "operational meaning and value-transfer rules remain unconfirmed"
        ),
        "next_validation": (
            "Seek source documentation or data-owner confirmation of how "
            "weight and freight should be interpreted when referenced from "
            "another record. Review the seven scheduled-date differences "
            "without copying or aggregating values automatically."
        ),
    },
    "DQ-07": {
        "evidence": (
            "There are 4,890 field-level reference occurrences across "
            "2,445 source records: 2,445 in weight and 2,445 in freight. "
            "Both fields point to the same target ID in all 2,445 records. "
            "All target IDs exist, and the extracted ASN/DN document number "
            "matches the target record's ASN/DN in every reference. No "
            "mismatches were found in the tested country, shipment mode, "
            "vendor, fulfilment method, product group, or delivered date "
            "fields. Seven source-target pairs have different scheduled "
            "dates, item descriptions, and quantities, but matching "
            "delivered dates. The references are internally consistent "
            "on the tested fields; their operational meaning and rules "
            "for transferring weight or freight remain unverified."
        ),
        "classification": (
            "Cross-record reference integrity validated for tested fields; "
            "business semantics unresolved"
        ),
        "validation_status": (
            "Target existence, shared target IDs, and ASN/DN document-number "
            "matches validated; reference meaning remains unconfirmed"
        ),
        "next_validation": (
            "Confirm whether references represent shipment-level values, "
            "shared values, or another documented convention. Assess jointly "
            "with DQ-06 and avoid double-counting the same underlying issue."
        ),
    },
}


def main():
    for path in REGISTER_FILES:
        if not path.exists():
            raise FileNotFoundError(f"Register not found: {path}")

    # Validate both files before changing either one.
    registers = {}
    for path in REGISTER_FILES:
        df = pd.read_csv(path, encoding="utf-8-sig")

        if "finding_id" not in df.columns:
            raise ValueError(f"'finding_id' column missing in {path.name}")

        if df["finding_id"].duplicated().any():
            raise ValueError(f"Duplicate finding IDs in {path.name}")

        for finding_id in UPDATES:
            if (df["finding_id"] == finding_id).sum() != 1:
                raise ValueError(
                    f"{finding_id} must appear exactly once in {path.name}"
                )

        registers[path] = df

    # Create backups before writing updates.
    for path in REGISTER_FILES:
        backup = path.with_name(
            f"{path.stem}.backup_before_reference_update.csv"
        )
        if backup.exists():
            raise FileExistsError(
                f"Backup already exists; review it before proceeding: {backup}"
            )
        registers[path].to_csv(backup, index=False, encoding="utf-8-sig")
        print(f"Backup created: {backup}")

    # Refresh only the specified evidence/status fields.
    for path, df in registers.items():
        for finding_id, fields in UPDATES.items():
            mask = df["finding_id"].eq(finding_id)

            for column, value in fields.items():
                if column in df.columns:
                    df.loc[mask, column] = value

        df.to_csv(path, index=False, encoding="utf-8-sig")
        print(f"Updated: {path}")

    print("\nUpdated findings: DQ-06 and DQ-07")
    print("Priorities and raw source data were not changed.")
    print("Review the backups and updated register files.")


if __name__ == "__main__":
    main()
