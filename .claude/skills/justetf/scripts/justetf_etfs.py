#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pandas>=2.2.0",
#     "pyyaml>=6.0",
#     "jinja2>=3.1",
#     "justetf-scraping @ git+https://github.com/patjlm/justetf-scraping.git@fix/etf-profile-bugs",
# ]
# ///
"""Search, filter, and manage ETF data from justETF.

Commands:
    search       Search/filter ETFs (supports --pea, --provider, --query, etc.)
    details      Get detailed profile for a single ETF by ISIN
    generate     Generate or update a single ETF markdown file
    bulk-update  Update all existing ETF markdown files from justETF data
"""

import argparse
import json
import random
import re
import sys
import time
from datetime import date
from pathlib import Path
from typing import Any

import jinja2
import justetf_scraping
import justetf_scraping.overview as ov
import yaml

MAX_RETRIES = 5
BASE_DELAY = 2.0
THROTTLE_DELAY = 1.0

def _find_repo_root() -> Path:
    p = Path(__file__).resolve()
    while p != p.parent:
        if (p / ".git").exists():
            return p
        p = p.parent
    raise RuntimeError("Could not find repo root (.git directory)")


REPO_ROOT = _find_repo_root()
DOCS_DIR = REPO_ROOT / "docs"
ETF_DIR = DOCS_DIR / "actifs" / "etf"
ETF_PEA_FILE = DOCS_DIR / "actifs" / "etf-eligibles-pea.md"
INDICES_DIR = DOCS_DIR / "actifs" / "indices"
CONTRATS_DIR = DOCS_DIR / "contrats"
TEMPLATE_PATH = REPO_ROOT / "skills" / "write-etf" / "assets" / "etf-template.md.j2"

REPLICATION_MAP = {
    "Full replication": "Physique",
    "Physical(Full replication)": "Physique",
    "Optimized sampling": "Échantillonnage",
    "Physical(Optimized sampling)": "Échantillonnage",
    "Unfunded swap": "Synthétique",
    "Synthetic(Unfunded swap)": "Synthétique",
    "Funded swap": "Synthétique",
    "Synthetic(Funded swap)": "Synthétique",
    "Swap based": "Synthétique",
    "Physically backed": "Adossé",
}

DISTRIBUTION_MAP = {
    "Accumulating": "Capitalisation",
    "Distributing": "Distribution",
}


def _retry_with_backoff(fn, *, label: str = ""):
    """Call fn() with exponential backoff + jitter on transient errors (403, 429, 5xx)."""
    for attempt in range(MAX_RETRIES):
        try:
            return fn()
        except Exception as e:
            status = ""
            for code in ("403", "429", "500", "502", "503", "504"):
                if code in str(e):
                    status = code
                    break
            if not status or attempt == MAX_RETRIES - 1:
                raise
            delay = BASE_DELAY * (2 ** attempt) + random.uniform(0, 1)
            print(f"  [{label}] {status} error (attempt {attempt + 1}/{MAX_RETRIES}), "
                  f"retrying in {delay:.1f}s...", file=sys.stderr)
            time.sleep(delay)
    raise RuntimeError("unreachable")


def _clean_html(val: str) -> str:
    return (val or "").replace("<br />", " ").replace("<br/>", " ").strip()


def _overview_for_isin(isin: str) -> dict[str, Any] | None:
    """Fetch overview data for a single ISIN (ticker, performances, volatility)."""
    try:
        rows = _retry_with_backoff(
            lambda: ov.load_raw_overview(local_country="FR", isin=isin),
            label=f"overview:{isin}",
        )
        if rows:
            return rows[0]
    except Exception as e:
        print(f"Overview lookup failed for {isin}: {e}", file=sys.stderr)
    return None


# ---------------------------------------------------------------------------
# Search & Details (existing commands)
# ---------------------------------------------------------------------------

def _search(args: argparse.Namespace) -> list[dict[str, Any]]:
    extra_params = ""
    if args.pea:
        extra_params += "&pea=true"
    if args.asset_class:
        extra_params += f"&assetClass=class-{args.asset_class}"

    if extra_params:
        _orig = ov.make_etf_params
        def _patched(*a, **kw):
            return _orig(*a, **kw) + extra_params
        ov.make_etf_params = _patched

    provider_filter = args.provider
    try:
        raw = ov.load_raw_overview(
            local_country="FR",
            region=args.region,
            provider=provider_filter,
            country=args.country,
        )
        if not raw and provider_filter:
            print(f"No results with provider='{provider_filter}', retrying without server filter...",
                  file=sys.stderr)
            raw = ov.load_raw_overview(
                local_country="FR",
                region=args.region,
                country=args.country,
            )
    finally:
        if extra_params:
            ov.make_etf_params = _orig

    results = []
    for etf in raw:
        results.append({
            "isin": etf.get("isin", ""),
            "name": etf.get("name", ""),
            "ter": etf.get("ter"),
            "size": etf.get("fundSize"),
            "domicile": etf.get("domicileCountry", ""),
            "currency": _clean_html(etf.get("fundCurrency", "")),
            "replication": _clean_html(etf.get("replicationMethod", "")),
            "distribution": etf.get("distributionPolicy", ""),
            "last_year": etf.get("yearReturnCUR"),
            "last_three_years": etf.get("threeYearReturnCUR"),
            "last_five_years": etf.get("fiveYearReturnCUR"),
            "holdings": etf.get("numberOfHoldings"),
        })

    if args.query:
        q = args.query.lower()
        results = [e for e in results if q in e["name"].lower() or q in e["isin"].lower()]

    if provider_filter and not args.provider_exact:
        pf = provider_filter.lower()
        results = [e for e in results if pf in e["name"].lower()]

    results.sort(key=lambda x: _parse_size(x.get("size")), reverse=True)

    if args.limit:
        results = results[:args.limit]

    return results


def _details(args_or_isin: argparse.Namespace | str) -> dict[str, Any]:
    isin = args_or_isin if isinstance(args_or_isin, str) else args_or_isin.isin

    profile = None
    try:
        profile = dict(_retry_with_backoff(
            lambda: justetf_scraping.get_etf_overview(
                isin, include_gettex=False, expand_allocations=False,
            ),
            label=f"profile:{isin}",
        ))
    except Exception as e:
        print(f"  Profile scraping failed: {e}", file=sys.stderr)
        profile = {}

    ov_data = _overview_for_isin(isin) or {}

    result = {
        "isin": (profile or {}).get("isin", isin),
        "name": (profile or {}).get("name") or ov_data.get("name"),
        "ticker": _clean_html(ov_data.get("ticker", "")),
        "description": (profile or {}).get("description"),
        "index": (profile or {}).get("index"),
        "ter": (profile or {}).get("ter") or ov_data.get("ter"),
        "fund_size_eur": (profile or {}).get("fund_size_eur") or ov_data.get("fundSize"),
        "replication": (profile or {}).get("replication") or _clean_html(ov_data.get("replicationMethod", "")),
        "distribution_policy": (profile or {}).get("distribution_policy") or ov_data.get("distributionPolicy"),
        "fund_currency": (profile or {}).get("fund_currency") or _clean_html(ov_data.get("fundCurrency", "")),
        "fund_domicile": (profile or {}).get("fund_domicile") or ov_data.get("domicileCountry"),
        "fund_provider": (profile or {}).get("fund_provider"),
        "inception_date": (profile or {}).get("inception_date"),
        "investment_focus": (profile or {}).get("investment_focus"),
        "sustainability": (profile or {}).get("sustainability"),
        "volatility_1y": (profile or {}).get("volatility_1y"),
        "last_year": ov_data.get("yearReturnCUR"),
        "last_three_years": ov_data.get("threeYearReturnCUR"),
        "last_five_years": ov_data.get("fiveYearReturnCUR"),
        "top_holdings": (profile or {}).get("top_holdings", []),
        "countries": (profile or {}).get("countries", []),
        "sectors": (profile or {}).get("sectors", []),
    }
    return result


def _parse_size(val: Any) -> int:
    if not val:
        return 0
    try:
        return int(str(val).replace(",", "").replace(".", "").strip())
    except (ValueError, TypeError):
        return 0


# ---------------------------------------------------------------------------
# Frontmatter & template helpers
# ---------------------------------------------------------------------------

def _parse_frontmatter(path: Path) -> dict[str, Any]:
    """Parse YAML frontmatter from a markdown file."""
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return {}
    end = content.index("\n---\n", 4)
    fm_str = content[4:end]
    return yaml.safe_load(fm_str) or {}


def _translate_replication(raw: str) -> str:
    for key, val in REPLICATION_MAP.items():
        if key.lower() in raw.lower():
            return val
    return "Non communiqué"


def _translate_distribution(raw: str) -> str:
    for key, val in DISTRIBUTION_MAP.items():
        if key.lower() in raw.lower():
            return val
    return "Non communiqué"


def _parse_ter(raw: Any) -> float | None:
    """Parse TER from various formats: 0.3, '0.30%', '0,30 %' -> 0.3."""
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        return float(raw) if raw > 0 else None
    s = str(raw).replace("%", "").replace(",", ".").strip()
    try:
        val = float(s)
        return val if val > 0 else None
    except ValueError:
        return None


def _format_ter(ter: float | str) -> str:
    """Format TER as French string: 0.2 -> '0,20 %'."""
    parsed = _parse_ter(ter)
    if parsed is None:
        return "Non communiqué"
    return f"{parsed:.2f} %".replace(".", ",")


def _load_pea_isins() -> set[str]:
    """Load PEA-eligible ISINs from docs/actifs/etf-eligibles-pea.md."""
    isin_re = re.compile(r"[A-Z]{2}[A-Z0-9]{9}\d")
    if not ETF_PEA_FILE.exists():
        return set()
    return set(isin_re.findall(ETF_PEA_FILE.read_text(encoding="utf-8")))


def _build_contrats_index() -> dict[str, list[dict[str, str]]]:
    """Scan all contrat files and build ISIN -> [{nom, lien}] mapping."""
    index: dict[str, list[dict[str, str]]] = {}
    isin_re = re.compile(r"[A-Z]{2}[A-Z0-9]{9}\d")
    for md_file in sorted(CONTRATS_DIR.rglob("*.md")):
        if md_file.name == "README.md":
            continue
        content = md_file.read_text(encoding="utf-8")
        fm = {}
        if content.startswith("---"):
            try:
                end = content.index("\n---\n", 4)
                fm = yaml.safe_load(content[4:end]) or {}
            except (ValueError, yaml.YAMLError):
                pass
        nom = fm.get("nom", md_file.stem)
        rel_path = Path("../../contrats") / md_file.relative_to(CONTRATS_DIR)
        for isin in set(isin_re.findall(content)):
            index.setdefault(isin, []).append({
                "nom": nom,
                "lien": str(rel_path),
            })
    for isins in index.values():
        isins.sort(key=lambda c: c["nom"])
    return index


def _build_indices_index() -> dict[str, str]:
    """Build index_name -> relative_path mapping from index files.

    Returns a dict mapping lowercase index names/slugs to relative paths
    from the ETF directory.
    """
    index: dict[str, str] = {}
    for md_file in sorted(INDICES_DIR.glob("*.md")):
        if md_file.name == "README.md":
            continue
        rel_path = f"../indices/{md_file.name}"
        slug = md_file.stem
        index[slug.lower()] = rel_path
        try:
            fm = _parse_frontmatter(md_file)
            nom = fm.get("nom", "")
            if nom:
                index[nom.lower()] = rel_path
        except Exception:
            pass
    return index


def _find_indice_lien(indice_name: str, indices_index: dict[str, str]) -> str | None:
    """Find the relative path to an index file matching the given index name."""
    if not indice_name:
        return None
    name_lower = indice_name.lower()
    if name_lower in indices_index:
        return indices_index[name_lower]
    slug = re.sub(r"[^a-z0-9]+", "-", name_lower).strip("-")
    if slug in indices_index:
        return indices_index[slug]
    for key, path in indices_index.items():
        if key in name_lower or name_lower in key:
            return path
    return None


def _load_template() -> jinja2.Template:
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(TEMPLATE_PATH.parent)),
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    return env.get_template(TEMPLATE_PATH.name)


def _render_etf(
    data: dict[str, Any],
    contrats: list[dict[str, str]],
    indice_lien: str | None,
    template: jinja2.Template,
    today: str,
) -> str:
    """Render a complete ETF markdown file from data."""
    try:
        ter = float(data.get("ter") or 0)
    except (ValueError, TypeError):
        ter = 0.0
    ctx = {
        "nom": data.get("nom", ""),
        "isin": data.get("isin", ""),
        "ticker": data.get("ticker", ""),
        "emetteur": data.get("emetteur", ""),
        "indice": data.get("indice", "Non communiqué"),
        "ter": ter,
        "ter_fmt": _format_ter(ter),
        "replication": data.get("replication", "Non communiqué"),
        "distribution": data.get("distribution", "Non communiqué"),
        "devise": data.get("devise", ""),
        "domicile": data.get("domicile", ""),
        "eligibilite_pea": data.get("eligibilite-pea", "non"),
        "sri": data.get("sri"),
        "date": today,
        "indice_lien": indice_lien,
        "contrats": contrats,
    }
    return template.render(**ctx)


def _normalize_details(details: dict[str, Any]) -> dict[str, Any]:
    """Convert justETF details response to frontmatter fields."""
    return {
        "nom": details.get("name", ""),
        "isin": details.get("isin", ""),
        "ticker": details.get("ticker", ""),
        "emetteur": details.get("fund_provider", ""),
        "indice": details.get("index", "Non communiqué"),
        "ter": details.get("ter") or 0,
        "replication": _translate_replication(details.get("replication", "")),
        "distribution": _translate_distribution(details.get("distribution_policy", "")),
        "devise": details.get("fund_currency", ""),
        "domicile": details.get("fund_domicile", ""),
        "sri": None,
    }


def _normalize_overview(ov_row: dict[str, Any]) -> dict[str, Any]:
    """Convert justETF overview row to frontmatter fields.

    Values that can't be parsed are set to None (not merged in bulk-update).
    """
    return {
        "nom": ov_row.get("name") or None,
        "isin": ov_row.get("isin", ""),
        "ticker": _clean_html(ov_row.get("ticker", "")) or None,
        "ter": _parse_ter(ov_row.get("ter")),
        "replication": _translate_replication(_clean_html(ov_row.get("replicationMethod", ""))),
        "distribution": _translate_distribution(ov_row.get("distributionPolicy", "")),
        "devise": _clean_html(ov_row.get("fundCurrency", "")) or None,
        "domicile": ov_row.get("domicileCountry") or None,
    }


# ---------------------------------------------------------------------------
# Generate & bulk-update commands
# ---------------------------------------------------------------------------

def _generate(args: argparse.Namespace) -> None:
    """Generate or update a single ETF markdown file."""
    isin = args.isin.upper()
    today = date.today().isoformat()
    etf_path = ETF_DIR / f"{isin}.md"

    print(f"Fetching details for {isin}...", file=sys.stderr)
    details = _details(isin)

    data = _normalize_details(details)

    pea_isins = _load_pea_isins()
    data["eligibilite-pea"] = "oui" if isin in pea_isins else "non"

    if etf_path.exists():
        existing_fm = _parse_frontmatter(etf_path)
        data["sri"] = existing_fm.get("sri")

    print("Building contrats index...", file=sys.stderr)
    contrats_index = _build_contrats_index()
    contrats = contrats_index.get(isin, [])

    indices_index = _build_indices_index()
    indice_lien = _find_indice_lien(data["indice"], indices_index)

    template = _load_template()
    content = _render_etf(data, contrats, indice_lien, template, today)

    ETF_DIR.mkdir(parents=True, exist_ok=True)
    etf_path.write_text(content, encoding="utf-8")
    print(f"{'Updated' if etf_path.exists() else 'Created'} {etf_path.relative_to(REPO_ROOT)}",
          file=sys.stderr)


def _bulk_update(args: argparse.Namespace) -> None:
    """Update all existing ETF markdown files from justETF overview data."""
    today = date.today().isoformat()

    etf_files = sorted(ETF_DIR.glob("*.md"))
    etf_files = [f for f in etf_files if f.name != "README.md"]
    if not etf_files:
        print("No ETF files found.", file=sys.stderr)
        return

    our_isins = {f.stem for f in etf_files}
    print(f"Found {len(our_isins)} ETF files to update.", file=sys.stderr)

    # Fetch all ETFs from justETF overview (single API call)
    print("Fetching justETF overview (all ETFs)...", file=sys.stderr)
    all_raw = _retry_with_backoff(
        lambda: ov.load_raw_overview(local_country="FR"),
        label="overview:all",
    )
    overview_by_isin = {etf["isin"]: etf for etf in all_raw}
    print(f"  {len(all_raw)} ETFs from justETF.", file=sys.stderr)

    # PEA eligibility from local file (no API call)
    pea_isins = _load_pea_isins()
    print(f"  {len(pea_isins)} PEA-eligible ISINs from {ETF_PEA_FILE.name}.", file=sys.stderr)

    # Build indexes (local file scanning)
    print("Building contrats index...", file=sys.stderr)
    contrats_index = _build_contrats_index()
    indices_index = _build_indices_index()
    template = _load_template()

    updated = 0
    skipped = 0
    not_found = 0

    for etf_file in etf_files:
        isin = etf_file.stem
        ov_row = overview_by_isin.get(isin)

        if not ov_row:
            print(f"  SKIP {isin}: not found in justETF overview", file=sys.stderr)
            not_found += 1
            continue

        existing_fm = _parse_frontmatter(etf_file)
        fresh = _normalize_overview(ov_row)

        data = dict(existing_fm)
        for key in ("nom", "ticker", "ter", "replication", "distribution", "devise", "domicile"):
            if fresh.get(key) is not None:
                data[key] = fresh[key]
        data["isin"] = isin
        data["eligibilite-pea"] = "oui" if isin in pea_isins else "non"

        contrats = contrats_index.get(isin, [])
        indice_lien = _find_indice_lien(data.get("indice", ""), indices_index)

        content = _render_etf(data, contrats, indice_lien, template, today)
        old_content = etf_file.read_text(encoding="utf-8")

        if content != old_content:
            etf_file.write_text(content, encoding="utf-8")
            updated += 1
        else:
            skipped += 1

    print(f"\nDone: {updated} updated, {skipped} unchanged, {not_found} not found in justETF.",
          file=sys.stderr)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    # search
    p = sub.add_parser("search", help="Search and filter ETFs")
    p.add_argument("--query", "-q", default="", help="Free text search (name or ISIN)")
    p.add_argument("--pea", action="store_true", help="PEA-eligible ETFs only")
    p.add_argument("--asset-class", help="Asset class (equity, bonds, commodities, etc.)")
    p.add_argument("--region", help="Region (World, Europe, North+America, etc.)")
    p.add_argument("--provider", help="ETF provider (Amundi, iShares, Xtrackers, etc.) — client-side filter by default")
    p.add_argument("--provider-exact", action="store_true", help="Use provider as server-side API filter (requires exact justETF name)")
    p.add_argument("--country", help="Target country (ISO alpha-2)")
    p.add_argument("--limit", type=int, help="Max results")
    p.add_argument("-o", "--output", help="Output JSON file (default: stdout)")

    # details
    p = sub.add_parser("details", help="Get detailed ETF profile")
    p.add_argument("isin", help="ISIN code")
    p.add_argument("-o", "--output", help="Output JSON file (default: stdout)")

    # generate
    p = sub.add_parser("generate", help="Generate or update a single ETF markdown file")
    p.add_argument("isin", help="ISIN code")

    # bulk-update
    p = sub.add_parser("bulk-update", help="Update all existing ETF markdown files")

    args = parser.parse_args()

    if args.command == "search":
        print("Fetching ETFs from justETF...", file=sys.stderr)
        data = _search(args)
        print(f"{len(data)} ETF trouvés", file=sys.stderr)
    elif args.command == "details":
        print(f"Fetching details for {args.isin}...", file=sys.stderr)
        data = _details(args)
    elif args.command == "generate":
        _generate(args)
        return
    elif args.command == "bulk-update":
        _bulk_update(args)
        return

    output = json.dumps(data, ensure_ascii=False, indent=2, default=str)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(output + "\n")
        print(f"Écrit dans {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
