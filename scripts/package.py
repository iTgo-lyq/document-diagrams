#!/usr/bin/env python3
"""Build a ZIP containing only the independently installable skill directory."""
import argparse
from pathlib import Path
import sys
from zipfile import ZIP_DEFLATED, ZipFile

from check import ROOT, SKILL, check_package


def build_package(output):
    output = Path(output).resolve()
    if output.is_relative_to(SKILL):
        raise ValueError("Write the archive outside the skill directory.")
    errors = check_package(SKILL)
    if errors:
        raise ValueError("\n".join(errors))
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
        for path in sorted(SKILL.rglob("*")):
            if path.is_file():
                archive.write(path, Path(SKILL.name) / path.relative_to(SKILL))
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist" / "document-diagrams.zip")
    args = parser.parse_args()
    try:
        output = build_package(args.output)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Created {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
