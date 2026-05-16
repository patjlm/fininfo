#!/usr/bin/env python3
"""Récupère les données de comparaison depuis simulateurs.sinvestir.fr via l'API Supabase."""

import argparse
import base64
import json
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError

SUPABASE_URL = "https://xtgfhotpcvykzxxtqzsn.supabase.co"
SUPABASE_ANON_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh0Z2Zob3RwY3Z5a3p4eHRxenNuIiwi"
    "cm9sZSI6ImFub24iLCJpYXQiOjE3NTQ3NDczODYsImV4cCI6MjA3MDMyMzM4Nn0."
    "edCbxNLVCac5bdTb0dq9weJe48Lb8nS3-ttyZYji-Bk"
)
COOKIE_PREFIX = "sb-xtgfhotpcvykzxxtqzsn-auth-token"

TYPES = [
    "per", "pea", "life-insurance", "scpi", "cto",
    "crypto", "online-bank", "online-bank-pro",
]


def find_cookie_file(explicit_path: str | None) -> Path:
    if explicit_path:
        p = Path(explicit_path)
        if not p.exists():
            print(f"Erreur : cookie.json introuvable : {p}", file=sys.stderr)
            sys.exit(1)
        return p
    candidates = [
        Path.cwd() / "cookie.json",
        Path.home() / ".config" / "findata" / "cookie.json",
    ]
    for p in candidates:
        if p.exists():
            return p
    print(
        "Erreur : cookie.json introuvable.\n"
        "Placez-le à la racine du projet ou passez --cookie-file.\n"
        "Pour l'obtenir : exportez les cookies de votre navigateur "
        "depuis https://simulateurs.sinvestir.fr/ (extension Cookie Quick Manager ou équivalent).",
        file=sys.stderr,
    )
    sys.exit(1)


def extract_access_token(cookie_file: Path) -> str:
    with open(cookie_file) as f:
        cookies = json.load(f)
    parts = {}
    for c in cookies:
        if c["name"] == f"{COOKIE_PREFIX}.0":
            parts[0] = c["value"]
        elif c["name"] == f"{COOKIE_PREFIX}.1":
            parts[1] = c["value"]
    if 0 not in parts:
        print(f"Erreur : cookie '{COOKIE_PREFIX}.0' introuvable dans {cookie_file}", file=sys.stderr)
        sys.exit(1)
    combined = parts[0] + parts.get(1, "")
    if combined.startswith("base64-"):
        combined = combined[7:]
    padding = 4 - len(combined) % 4
    if padding != 4:
        combined += "=" * padding
    decoded = base64.b64decode(combined)
    data = json.loads(decoded)
    token = data.get("access_token")
    if not token:
        print("Erreur : access_token absent du cookie décodé.", file=sys.stderr)
        sys.exit(1)
    return token


def fetch_comparisons(access_token: str, comparison_type: str, active_only: bool = True) -> list[dict]:
    params = f"type=eq.{comparison_type}&order=name"
    if active_only:
        params += "&is_active=eq.true"
    url = f"{SUPABASE_URL}/rest/v1/comparisons?{params}"
    req = Request(url)
    req.add_header("apikey", SUPABASE_ANON_KEY)
    req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("Content-Type", "application/json")
    try:
        with urlopen(req) as resp:
            return json.loads(resp.read())
    except HTTPError as e:
        body = e.read().decode()
        print(f"Erreur API ({e.code}) : {body}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("type", choices=TYPES, help="Type de comparaison à récupérer")
    parser.add_argument("--cookie-file", help="Chemin vers cookie.json (défaut : ./cookie.json)")
    parser.add_argument("--include-inactive", action="store_true", help="Inclure les entrées inactives")
    parser.add_argument("--output", "-o", help="Fichier de sortie (défaut : stdout)")
    args = parser.parse_args()

    cookie_file = find_cookie_file(args.cookie_file)
    access_token = extract_access_token(cookie_file)
    data = fetch_comparisons(access_token, args.type, active_only=not args.include_inactive)

    output = json.dumps(data, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output + "\n")
        print(f"{len(data)} résultats écrits dans {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
