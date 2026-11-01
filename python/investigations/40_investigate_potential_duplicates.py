
from pathlib import Path
import pandas as pd

BASE = Path(r"C:\Project_03")
SOURCE = BASE / "dataset" / "Suppy_Chain_Shipment_Data.csv"
OUTPUT = BASE / "publication" / "execution" / "outputs"

OUTPUT.mkdir(parents=True, exist_ok=True)

RECORDS_OUT = OUTPUT / "potential_duplicate_records.csv"
GROUPS_OUT = OUTPUT / "potential_duplicate_groups.csv"


def main():
    df = pd.read_csv(SOURCE, low_memory=False)

    if "id" not in df.columns:
        raise ValueError("Expected an 'id' column in the source dataset.")

    if df["id"].isna().any():
        raise ValueError("Source IDs contain missing values; investigate first.")

    if df["id"].duplicated().any():
        raise ValueError("Source IDs are not unique; investigate first.")

    # Match records on every field except the unique record identifier.
    compare_cols = [c for c in df.columns if c != "id"]

    # dropna=False ensures missing values are treated consistently
    # when identifying matching records.
    duplicate_mask = df.duplicated(
        subset=compare_cols,
        keep=False
    )

    candidates = df.loc[duplicate_mask].copy()

    if candidates.empty:
        candidates["candidate_group"] = pd.Series(dtype="int64")
        groups = pd.DataFrame(
            columns=[
                "candidate_group",
                "record_count",
                "source_ids",
                "matching_fields_count",
            ]
        )
    else:
        # Give identical non-ID signatures a stable group number
        # within this source-file version.
        signatures = candidates[compare_cols].copy()
        group_codes, _ = pd.factorize(
            pd.MultiIndex.from_frame(signatures),
            sort=True
        )
        candidates["candidate_group"] = group_codes + 1

        group_rows = []
        for group_id, group in candidates.groupby(
            "candidate_group", sort=True
        ):
            group_rows.append({
                "candidate_group": int(group_id),
                "record_count": len(group),
                "source_ids": " | ".join(
                    group["id"].astype(str).tolist()
                ),
                "matching_fields_count": len(compare_cols),
            })

        groups = pd.DataFrame(group_rows)

    candidates.to_csv(RECORDS_OUT, index=False)
    groups.to_csv(GROUPS_OUT, index=False)

    print(f"Source shape: {df.shape}")
    print(f"Fields compared (excluding ID): {len(compare_cols)}")
    print(f"Candidate duplicate records: {len(candidates)}")
    print(f"Candidate duplicate groups: {len(groups)}")
    print(f"\nRecords output: {RECORDS_OUT}")
    print(f"Groups output: {GROUPS_OUT}")

    print("\nCandidate groups:")
    if groups.empty:
        print("No candidate duplicate groups found.")
    else:
        print(groups.to_string(index=False))


if __name__ == "__main__":
    main()
