from __future__ import annotations

import re
from pathlib import Path


RE_SCHEDULE = re.compile(
    r"^ASN AV[_ ](?P<weekly>\d+)\s*Std_(?P<days>\d+)\s*Tage-(?P<daily>\d+)\s*Std_(?P<role>.+)$"
)
RE_SIMPLE = re.compile(r"^ASN AV[_ ](?P<weekly>\d+)[_ ]Std_(?P<role>.+)$")
RE_SIMPLE_ALT = re.compile(r"^ASN AV[_ ](?P<weekly>\d+)_Std_(?P<role>.+)$")


def normalize_role(role: str) -> str:
    # Keep umlauts etc, but make it filename-consistent.
    role = role.replace(".", "")
    role = re.sub(r"\s+", "_", role.strip())
    role = re.sub(r"_+", "_", role)
    return role.strip("_")


def main() -> int:
    base_dir = Path(__file__).resolve().parents[1]
    wien_dir = base_dir / "contracts" / "wien"
    if not wien_dir.exists():
        raise FileNotFoundError(f"Missing folder: {wien_dir}")

    files = sorted(wien_dir.glob("*.docx"))
    renamed: list[tuple[str, str]] = []

    for path in files:
        stem = path.stem
        if stem.startswith("ASN_AV_wien_"):
            continue

        m = RE_SCHEDULE.match(stem) or RE_SIMPLE.match(stem) or RE_SIMPLE_ALT.match(stem)
        if not m:
            raise ValueError(f"Unrecognized Wien template name: {path.name}")

        weekly = m.group("weekly")
        role = normalize_role(m.group("role"))

        if "days" in m.groupdict() and m.group("days") and m.group("daily"):
            days = m.group("days")
            daily = m.group("daily")
            new_name = f"ASN_AV_wien_{role}_{weekly}_Std_{days}_Tage_{daily}_Std.docx"
        else:
            new_name = f"ASN_AV_wien_{role}_{weekly}_Std.docx"

        target = path.with_name(new_name)
        if target.exists():
            raise FileExistsError(f"Rename collision: {target.name} already exists")

        path.rename(target)
        renamed.append((path.name, target.name))

    if renamed:
        print("Renamed:")
        for old, new in renamed:
            print(f" - {old} -> {new}")
    else:
        print("No files needed renaming.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

