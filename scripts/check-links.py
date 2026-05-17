#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Vérifie que tous les liens markdown internes pointent vers des fichiers existants."""

import re
import sys
from pathlib import Path

LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
DOCS_DIR = Path("docs")


def check_file(md_file: Path) -> list[str]:
    errors = []
    for line_no, line in enumerate(md_file.read_text().splitlines(), start=1):
        for match in LINK_RE.finditer(line):
            target = match.group(2)
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = target.split("#")[0]
            if not target:
                continue
            resolved = (md_file.parent / target).resolve()
            if resolved.is_dir():
                if not (resolved / "README.md").exists():
                    errors.append(f"{md_file}:{line_no}: répertoire sans README.md → {target}")
            elif not resolved.is_file():
                errors.append(f"{md_file}:{line_no}: lien cassé → {target}")
    return errors


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else DOCS_DIR
    md_files = sorted(root.rglob("*.md"))
    if not md_files:
        print(f"Aucun fichier .md trouvé dans {root}", file=sys.stderr)
        return 1

    all_errors = []
    for f in md_files:
        all_errors.extend(check_file(f))

    if all_errors:
        print(f"{len(all_errors)} lien(s) cassé(s) :\n")
        for err in all_errors:
            print(f"  {err}")
        return 1

    print(f"{len(md_files)} fichiers vérifiés, aucun lien cassé.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
