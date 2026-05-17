#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml>=6.0"]
# ///
"""Valide le frontmatter YAML des fiches docs/ contre les templates des skills.

Les champs obligatoires sont extraits automatiquement du frontmatter de chaque
template dans .claude/skills/*/assets/*-template*.md. Chaque template définit
un `type` qui sert de clé de correspondance.

Vérifications :
- Champs obligatoires présents (définis par le template du type correspondant)
- `derniere-mise-a-jour` au format YYYY-MM-DD valide
- `slug` correspond au nom de fichier (sans .md)
- `type` reconnu (a un template associé)
"""

import re
import sys
from datetime import date
from pathlib import Path

import yaml

DOCS_DIR = Path("docs")
SKILLS_DIR = Path(".claude/skills")
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


def parse_frontmatter(text: str) -> dict | None:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    try:
        data = yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return None
    if not isinstance(data, dict):
        return None
    return data


def load_schemas() -> dict[str, list[str]]:
    schemas = {}
    for template in sorted(SKILLS_DIR.rglob("*template*.md")):
        fm = parse_frontmatter(template.read_text())
        if not fm or "type" not in fm:
            continue
        schemas[fm["type"]] = list(fm.keys())
    return schemas


def validate_date(value) -> bool:
    try:
        if isinstance(value, date):
            return True
        date.fromisoformat(str(value))
        return True
    except (ValueError, TypeError):
        return False


def check_file(md_file: Path, schemas: dict[str, list[str]]) -> list[str]:
    errors = []
    fm = parse_frontmatter(md_file.read_text())
    if fm is None:
        return []

    file_type = fm.get("type", "")
    if not file_type:
        errors.append(f"{md_file}: champ 'type' manquant")
        return errors

    if file_type not in schemas:
        errors.append(f"{md_file}: type '{file_type}' sans template")
        return errors

    for key in schemas[file_type]:
        if key not in fm or fm[key] is None or fm[key] == "":
            errors.append(f"{md_file}: champ '{key}' manquant (requis par template {file_type})")

    d = fm.get("derniere-mise-a-jour")
    if d is not None and not validate_date(d):
        errors.append(f"{md_file}: derniere-mise-a-jour invalide '{d}' (attendu YYYY-MM-DD)")

    slug = fm.get("slug")
    if slug and str(slug) != md_file.stem:
        errors.append(f"{md_file}: slug '{slug}' != nom de fichier '{md_file.stem}'")

    return errors


def main() -> int:
    schemas = load_schemas()
    if not schemas:
        print("Aucun template trouvé", file=sys.stderr)
        return 1

    print(f"Schemas chargés : {', '.join(sorted(schemas.keys()))}", file=sys.stderr)

    root = Path(sys.argv[1]) if len(sys.argv) > 1 else DOCS_DIR
    md_files = sorted(root.rglob("*.md"))

    all_errors = []
    checked = 0
    skipped_no_fm = 0
    skipped_unknown = 0

    for f in md_files:
        errs = check_file(f, schemas)
        if errs:
            for e in errs:
                if "sans template" in e:
                    skipped_unknown += 1
                else:
                    all_errors.append(e)
        else:
            if parse_frontmatter(f.read_text()) is None:
                skipped_no_fm += 1
            else:
                checked += 1

    print(f"{checked} fiches validées, {skipped_no_fm} sans frontmatter, "
          f"{skipped_unknown} type(s) sans template", file=sys.stderr)

    if all_errors:
        print(f"\n{len(all_errors)} erreur(s) de frontmatter :\n")
        for err in all_errors:
            print(f"  {err}")
        return 1

    print("Aucune erreur de frontmatter.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
