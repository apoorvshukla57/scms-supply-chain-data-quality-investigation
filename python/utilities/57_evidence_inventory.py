
from pathlib import Path

OUT = Path(r"C:\Project_03\publication\evidence")

print("PROJECT 03 — PUBLICATION EVIDENCE INVENTORY")
print("=" * 72)

if not OUT.exists():
    raise FileNotFoundError(f"Output directory not found: {OUT}")

files = sorted(
    (p for p in OUT.iterdir() if p.is_file()),
    key=lambda p: p.name.lower()
)

print(f"Output directory: {OUT}")
print(f"Files found: {len(files)}\n")

for path in files:
    print(f"{path.name:<55} {path.stat().st_size:>12,} bytes")

print("\nInventory complete. No files were modified.")
