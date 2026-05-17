#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Récupère la liste complète des fonds d'un contrat Linxea via l'API Morningstar.

Utilise les credentials publics embarqués dans le bundle JS de Linxea X-Ray.
"""

import argparse
import json
import math
import sys
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError

TOKEN_URL = "https://www.emea-api.morningstar.com/token/oauth"
SCREENER_URL = "https://www.emea-api.morningstar.com/ecint/v1/screener"

# Base64(ec-Linxe-2022@eamsecservice.com:LinxeB*j91) — public, embedded in Linxea JS bundle
SERVICE_CREDENTIALS = "ZWMtTGlueGUtMjAyMkBlYW1zZWNzZXJ2aWNlLmNvbTpMaW54ZUIqajkx"

SECURITY_DATA_POINTS = "|".join([
    "name", "LegalName", "ISIN", "SecId",
    "CategoryName", "GlobalCategoryName", "GlobalAssetClassName",
    "StarRating", "KID_SRI", "KID_OngoingOtherCosts",
    "ManagementFee", "PerformanceFee",
    "ReturnM1", "ReturnM3", "ReturnM6", "ReturnM12",
    "ReturnM36", "ReturnM60", "ReturnM120",
    "StandardDeviationM36", "SharpeM36", "MaxDrawdownM12",
    "FundTNAV", "EET_EUSFDRType", "universe",
    "ExchangeTradedShare",
])

UNIVERSES = {
    "per_spirit": "FEEUR$$ALL_5650",
    "spirit_2": "FEEUR$$ALL_5627",
    "spirit_capi_2": "FEEUR$$ALL_5628",
    "spirit": "FEEUR$$ALL_1426",
    "suravenir_per": "FEEUR$$ALL_5649",
    "per": "FEEUR$$ALL_5252",
    "avenir": "FEEUR$$ALL_1016",
    "avenir_2": "FEEUR$$ALL_7170",
    "vie": "FEEUR$$ALL_842",
    "zen": "FEEUR$$ALL_2659",
}

PAGE_SIZE = 100


def obtain_bearer_token() -> str:
    req = Request(TOKEN_URL, data=b"", method="POST")
    req.add_header("Authorization", f"Basic {SERVICE_CREDENTIALS}")
    try:
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            token = data.get("access_token", "")
            if not token:
                print("Erreur : pas d'access_token dans la réponse", file=sys.stderr)
                sys.exit(1)
            print(f"Token obtenu (expire dans {data.get('expires_in', '?')}s)", file=sys.stderr)
            return token
    except HTTPError as e:
        print(f"Erreur token ({e.code}) : {e.read().decode()}", file=sys.stderr)
        sys.exit(1)


def get(row: dict, key: str, default=None):
    val = row.get(key)
    if val is None:
        return default
    if isinstance(val, dict):
        val = val.get("value")
        if val is None:
            return default
    if isinstance(val, str) and val == "":
        return default
    return val


def to_float(val):
    if val is None:
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def is_etf(row: dict) -> bool:
    ets = get(row, "ExchangeTradedShare")
    if ets is not None:
        if isinstance(ets, bool):
            return ets
        if isinstance(ets, str):
            return ets.lower() in ("true", "1", "yes")
    name = f"{get(row, 'name', '')} {get(row, 'LegalName', '')}".upper()
    return " ETF " in f" {name} " or " ETC " in f" {name} "


def normalise(row: dict) -> dict | None:
    isin = get(row, "ISIN")
    if not isin:
        return None
    return {
        "isin": str(isin),
        "name": str(get(row, "name", "")),
        "legal_name": str(get(row, "LegalName", "")),
        "category": str(get(row, "CategoryName", "")),
        "global_category": str(get(row, "GlobalCategoryName", "")),
        "asset_class": str(get(row, "GlobalAssetClassName", "")),
        "star_rating": get(row, "StarRating"),
        "srri": get(row, "KID_SRI"),
        "ongoing_charge": to_float(get(row, "KID_OngoingOtherCosts")),
        "management_fee": to_float(get(row, "ManagementFee")),
        "performance_fee": to_float(get(row, "PerformanceFee")),
        "return_1y": to_float(get(row, "ReturnM12")),
        "return_3y": to_float(get(row, "ReturnM36")),
        "return_5y": to_float(get(row, "ReturnM60")),
        "fund_size": to_float(get(row, "FundTNAV")),
        "sfdr_type": str(get(row, "EET_EUSFDRType", "")),
        "is_etf": is_etf(row),
    }


def fetch_universe(token: str, universe_id: str) -> list[dict]:
    page = 1
    all_funds = []
    total = None

    while True:
        query = urlencode({
            "languageId": "fr-FR",
            "universeIds": universe_id,
            "outputType": "json",
            "securityDataPoints": SECURITY_DATA_POINTS,
            "sortOrder": "LegalName asc",
            "page": str(page),
            "pageSize": str(PAGE_SIZE),
        })
        req = Request(f"{SCREENER_URL}?{query}")
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Accept", "application/json")
        req.add_header("Origin", "https://www.linxea.com")
        req.add_header("Referer", "https://www.linxea.com/")

        try:
            with urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
        except HTTPError as e:
            print(f"Erreur screener ({e.code}) : {e.read().decode()}", file=sys.stderr)
            sys.exit(1)

        rows = data.get("rows", [])
        if total is None:
            total = int(data.get("total", 0))
            total_pages = math.ceil(total / PAGE_SIZE) if total else 1
            print(f"{total} fonds, {total_pages} pages", file=sys.stderr)

        for row in rows:
            fund = normalise(row)
            if fund:
                all_funds.append(fund)

        print(f"  page {page} — {len(all_funds)} fonds", file=sys.stderr)

        if page * PAGE_SIZE >= total:
            break
        page += 1

    return all_funds


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", choices=list(UNIVERSES.keys()), help="Contrat Linxea")
    parser.add_argument("--output", "-o", help="Fichier de sortie JSON")
    parser.add_argument("--etf-only", action="store_true", help="Filtrer ETF uniquement")
    args = parser.parse_args()

    universe_id = UNIVERSES[args.contract]

    print(f"Obtention du token Morningstar...", file=sys.stderr)
    token = obtain_bearer_token()

    print(f"Récupération {args.contract} ({universe_id})...", file=sys.stderr)
    funds = fetch_universe(token, universe_id)

    if args.etf_only:
        funds = [f for f in funds if f.get("is_etf")]

    etf_count = sum(1 for f in funds if f.get("is_etf"))
    opcvm_count = len(funds) - etf_count
    print(f"Total : {len(funds)} fonds (ETF : {etf_count}, OPCVM : {opcvm_count})", file=sys.stderr)

    output = json.dumps(funds, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(output + "\n")
        print(f"Écrit dans {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
