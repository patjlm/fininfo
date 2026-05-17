#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml>=6.0"]
# ///
"""Génère les tableaux comparatifs dans les README.md depuis le frontmatter.

Pour chaque sous-dossier de docs/ contenant des fiches typées, le script :
1. Lit le frontmatter de tous les fichiers .md (sauf README.md)
2. Génère un tableau markdown avec les colonnes définies par type
3. Écrit le résultat entre les marqueurs <!-- BEGIN GENERATED --> / <!-- END GENERATED -->

Usage :
  uv run scripts/generate-readmes.py          # génère les README
  uv run scripts/generate-readmes.py --check   # vérifie sans modifier (CI)
"""

import re
import sys
from datetime import date
from pathlib import Path

import yaml

DOCS_DIR = Path("docs")
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)

BEGIN_MARKER = "<!-- BEGIN GENERATED -->"
END_MARKER = "<!-- END GENERATED -->"

COLUMNS: dict[str, list[tuple[str, str]]] = {
    "contrat-per": [
        ("Contrat", "nom"),
        ("Distributeur", "distributeur"),
        ("Assureur", "assureur"),
        ("Frais versement", "frais-versement"),
        ("Frais gestion UC", "frais-gestion-uc"),
        ("Frais arbitrage", "frais-arbitrage"),
    ],
    "contrat-assurance-vie": [
        ("Contrat", "nom"),
        ("Distributeur", "distributeur"),
        ("Assureur", "assureur"),
        ("Frais versement", "frais-versement"),
        ("Frais gestion UC", "frais-gestion-uc"),
        ("Frais arbitrage", "frais-arbitrage"),
    ],
    "contrat-pea": [
        ("Courtier", "nom"),
        ("Pays", "_body"),
        ("Gestion", "_body"),
    ],
    "contrat-cto": [
        ("Courtier", "nom"),
    ],
    "etf": [
        ("Nom", "nom"),
        ("ISIN", "isin"),
        ("Ticker", "ticker"),
        ("Indice", "indice"),
        ("TER", "ter"),
        ("Rép.", "replication"),
        ("Dist.", "distribution"),
        ("PEA", "eligibilite-pea"),
    ],
    "scpi": [
        ("Nom", "nom"),
        ("Société de gestion", "societe-de-gestion"),
        ("Catégorie", "categorie"),
        ("Capital", "capital"),
        ("Prix part", "prix-de-part"),
        ("Rendement", "taux-de-distribution"),
        ("ISR", "label-isr"),
    ],
}


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


def fmt_value(value, field: str) -> str:
    if value is None or value == "":
        return "—"
    if field == "ter" and isinstance(value, (int, float)):
        return f"{value:.2f} %"
    if field == "taux-de-distribution" and isinstance(value, (int, float)):
        return f"{value:.2f} %"
    if field == "prix-de-part" and isinstance(value, (int, float)):
        return f"{value:,.0f} EUR".replace(",", " ")
    if field in ("frais-versement", "frais-gestion-uc", "frais-arbitrage"):
        if isinstance(value, (int, float)):
            formatted = f"{value:g}"
            return f"{formatted} %"
        if isinstance(value, str):
            return value
    if isinstance(value, date):
        return str(value)
    return str(value)


def generate_table(directory: Path, file_type: str) -> str | None:
    cols = COLUMNS.get(file_type)
    if not cols:
        return None

    usable_cols = [(label, field) for label, field in cols if not field.startswith("_")]

    entries = []
    for md_file in sorted(directory.glob("*.md")):
        if md_file.name == "README.md":
            continue
        fm = parse_frontmatter(md_file.read_text())
        if not fm or fm.get("type") != file_type:
            continue
        entries.append((md_file, fm))

    if not entries:
        return None

    headers = [label for label, _ in usable_cols]
    header_line = "| " + " | ".join(headers) + " |"
    sep_line = "|" + "|".join("---" for _ in usable_cols) + "|"

    rows = []
    for md_file, fm in entries:
        cells = []
        for i, (_, field) in enumerate(usable_cols):
            val = fm.get(field, None)
            formatted = fmt_value(val, field)
            if i == 0:
                formatted = f"[{formatted}]({md_file.name})"
            cells.append(formatted)
        rows.append("| " + " | ".join(cells) + " |")

    return "\n".join([header_line, sep_line, *rows])


def detect_type(directory: Path) -> str | None:
    for md_file in directory.glob("*.md"):
        if md_file.name == "README.md":
            continue
        fm = parse_frontmatter(md_file.read_text())
        if fm and "type" in fm:
            return fm["type"]
    return None


def update_readme(directory: Path, table: str, check_only: bool) -> bool:
    readme = directory / "README.md"
    if not readme.exists():
        return False

    content = readme.read_text()

    if BEGIN_MARKER in content and END_MARKER in content:
        before = content[: content.index(BEGIN_MARKER)]
        after = content[content.index(END_MARKER) + len(END_MARKER) :]
        new_content = f"{before}{BEGIN_MARKER}\n{table}\n{END_MARKER}{after}"
    else:
        new_content = content.rstrip() + f"\n\n{BEGIN_MARKER}\n{table}\n{END_MARKER}\n"

    if new_content == content:
        return True

    if check_only:
        return False

    readme.write_text(new_content)
    return True


def find_typed_directories() -> list[tuple[Path, str]]:
    result = []
    for directory in sorted(DOCS_DIR.rglob("*")):
        if not directory.is_dir():
            continue
        file_type = detect_type(directory)
        if file_type and file_type in COLUMNS:
            result.append((directory, file_type))
    return result


def main() -> int:
    check_only = "--check" in sys.argv

    dirs = find_typed_directories()
    if not dirs:
        print("Aucun répertoire typé trouvé", file=sys.stderr)
        return 1

    updated = 0
    stale = 0
    skipped = 0

    for directory, file_type in dirs:
        table = generate_table(directory, file_type)
        if not table:
            skipped += 1
            continue

        readme = directory / "README.md"
        if not readme.exists():
            skipped += 1
            continue

        ok = update_readme(directory, table, check_only)
        if ok:
            updated += 1
        else:
            stale += 1
            rel = readme.relative_to(Path.cwd()) if readme.is_relative_to(Path.cwd()) else readme
            print(f"  {rel}: tableau non à jour", file=sys.stderr)

    action = "vérifiés" if check_only else "mis à jour"
    print(f"{updated} README {action}, {skipped} ignorés", file=sys.stderr)

    if stale:
        print(f"\n{stale} README non à jour. Exécuter : make readmes")
        return 1

    print("Tous les README sont à jour.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
