#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml>=6.0"]
# ///
"""Valide le frontmatter YAML des fiches docs/ contre les schemas des skills.

Les schemas sont chargés depuis .claude/skills/*/assets/schema-*.yaml.
Chaque schema définit un `type` et ses champs avec required, type, et values (enum).

Vérifications :
- Champs obligatoires présents (required: true dans le schema)
- Types de valeurs corrects (string, number, date, enum)
- Valeurs enum autorisées
- `derniere-verification` au format YYYY-MM-DD valide
- `slug` correspond au nom de fichier (sans .md)
- `type` reconnu (a un schema associé)

Rétrocompatibilité : si aucun schema n'existe pour un type, les champs requis
sont extraits du template correspondant (fallback).
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


def load_schemas() -> dict[str, dict]:
    """Charge les schemas depuis schema-*.yaml, avec fallback sur les templates."""
    schemas: dict[str, dict] = {}

    for schema_file in sorted(SKILLS_DIR.rglob("schema-*.yaml")):
        try:
            data = yaml.safe_load(schema_file.read_text())
        except yaml.YAMLError:
            continue
        if not isinstance(data, dict) or "type" not in data or "fields" not in data:
            continue
        schemas[data["type"]] = data["fields"]

    for template in sorted(SKILLS_DIR.rglob("*template*.md")):
        fm = parse_frontmatter(template.read_text())
        if not fm or "type" not in fm:
            continue
        if fm["type"] not in schemas:
            schemas[fm["type"]] = {
                key: {"required": True, "type": "string"} for key in fm
            }

    return schemas


def validate_date(value) -> bool:
    try:
        if isinstance(value, date):
            return True
        date.fromisoformat(str(value))
        return True
    except (ValueError, TypeError):
        return False


def validate_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def check_file(md_file: Path, schemas: dict[str, dict]) -> list[str]:
    errors = []
    fm = parse_frontmatter(md_file.read_text())
    if fm is None:
        return []

    file_type = fm.get("type", "")
    if not file_type:
        errors.append(f"{md_file}: champ 'type' manquant")
        return errors

    if file_type not in schemas:
        errors.append(f"{md_file}: type '{file_type}' sans schema")
        return errors

    schema = schemas[file_type]

    for key, spec in schema.items():
        value = fm.get(key)
        is_required = spec.get("required", True) if isinstance(spec, dict) else True

        if value is None or value == "":
            if is_required:
                errors.append(f"{md_file}: champ '{key}' manquant (requis)")
            continue

        if not isinstance(spec, dict):
            continue

        if str(value) == "Non communiqué":
            continue

        field_type = spec.get("type", "string")

        if field_type == "date" and not validate_date(value):
            errors.append(f"{md_file}: '{key}' invalide '{value}' (attendu YYYY-MM-DD)")

        elif field_type == "number" and not validate_number(value):
            errors.append(f"{md_file}: '{key}' invalide '{value}' (attendu nombre)")

        elif field_type == "enum":
            allowed = spec.get("values", [])
            if str(value) not in [str(v) for v in allowed]:
                errors.append(
                    f"{md_file}: '{key}' valeur '{value}' non autorisée "
                    f"(attendu: {', '.join(str(v) for v in allowed)})"
                )

    slug = fm.get("slug")
    if slug and str(slug) != md_file.stem:
        errors.append(f"{md_file}: slug '{slug}' != nom de fichier '{md_file.stem}'")

    return errors


def main() -> int:
    schemas = load_schemas()
    if not schemas:
        print("Aucun schema trouvé", file=sys.stderr)
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
                if "sans schema" in e:
                    skipped_unknown += 1
                else:
                    all_errors.append(e)
        else:
            if parse_frontmatter(f.read_text()) is None:
                skipped_no_fm += 1
            else:
                checked += 1

    print(f"{checked} fiches validées, {skipped_no_fm} sans frontmatter, "
          f"{skipped_unknown} type(s) sans schema", file=sys.stderr)

    if all_errors:
        print(f"\n{len(all_errors)} erreur(s) de frontmatter :\n")
        for err in all_errors:
            print(f"  {err}")
        return 1

    print("Aucune erreur de frontmatter.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
