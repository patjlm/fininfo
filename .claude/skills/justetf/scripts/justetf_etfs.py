#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pandas>=2.2.0",
#     "justetf-scraping @ git+https://github.com/patjlm/justetf-scraping.git@fix/etf-profile-bugs",
# ]
# ///
"""Search, filter, and get details on ETFs from justETF.

Commands:
    search   Search/filter ETFs (supports --pea, --provider, --query, etc.)
    details  Get detailed profile for a single ETF by ISIN
"""

import argparse
import json
import random
import sys
import time
from pathlib import Path
from typing import Any

import justetf_scraping
import justetf_scraping.overview as ov

MAX_RETRIES = 5
BASE_DELAY = 2.0


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

    # Provider is passed to the API but requires the exact justETF name
    # (e.g. "BNP Paribas Easy", not "BNP Paribas"). If the API returns 0
    # results, fall back to client-side filtering without the provider param.
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


def _details(args: argparse.Namespace) -> dict[str, Any]:
    # 1. Profile scraping (holdings, allocations, description)
    profile = None
    try:
        profile = dict(_retry_with_backoff(
            lambda: justetf_scraping.get_etf_overview(
                args.isin, include_gettex=False, expand_allocations=False,
            ),
            label=f"profile:{args.isin}",
        ))
    except Exception as e:
        print(f"  Profile scraping failed: {e}", file=sys.stderr)
        profile = {}

    # 2. Overview API (ticker, performances, volatility)
    ov_data = _overview_for_isin(args.isin) or {}

    result = {
        "isin": (profile or {}).get("isin", args.isin),
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

    args = parser.parse_args()

    if args.command == "search":
        print("Fetching ETFs from justETF...", file=sys.stderr)
        data = _search(args)
        print(f"{len(data)} ETF trouvés", file=sys.stderr)
    elif args.command == "details":
        print(f"Fetching details for {args.isin}...", file=sys.stderr)
        data = _details(args)

    output = json.dumps(data, ensure_ascii=False, indent=2, default=str)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(output + "\n")
        print(f"Écrit dans {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()