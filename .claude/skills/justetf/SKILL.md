---
name: justetf
description: >-
  Récupérer des données ETF depuis justETF et générer les fiches markdown.
  Rechercher/filtrer des ETF, obtenir les détails, générer ou mettre à
  jour les fiches ETF (une par une ou en masse).
allowed-tools: Read Write Edit Bash
---

# Récupérer des données ETF depuis justETF

## Bibliothèque : `justetf-scraping`

Dépendance GitHub uniquement (pas sur PyPI). Le script utilise des inline script dependencies pour `uv run`.

### Fonctions clés

| Fonction | Retour | Notes |
|---|---|---|
| `load_overview()` | `pd.DataFrame` | ~4000 ETF, lent (~2 min), ISIN = index |
| `get_etf_overview(isin)` | `EtfOverview` | Profil + holdings via scraping HTML |
| `load_chart(isin)` | `pd.DataFrame` | Historique de prix complet |

### Bugs connus

- `get_etf_overview(include_gettex=True)` → `NameError` — toujours utiliser `include_gettex=False`
- `expand_allocations=True` retourne des listes vides — parsing AJAX cassé

### Conventions de données

- **TER** : points de pourcentage (0.2 = 0,20 %)
- **Taille du fonds** : en millions EUR
- **Rendements** : points de pourcentage
- **Index du DataFrame overview** : ISIN (pas une colonne)

## Script générique

```bash
uv run skills/justetf/scripts/justetf_etfs.py <commande> [options]
```

### Commandes

#### `search` — Rechercher des ETF

```bash
# Tous les ETF éligibles PEA
uv run skills/justetf/scripts/justetf_etfs.py search --pea -o .tmp/pea-etfs.json

# ETF d'un émetteur spécifique
uv run skills/justetf/scripts/justetf_etfs.py search --provider Amundi --pea

# Limiter les résultats
uv run skills/justetf/scripts/justetf_etfs.py search --pea --limit 20

# Recherche textuelle
uv run skills/justetf/scripts/justetf_etfs.py search --query "MSCI World"
```

#### `details` — Détails d'un ETF

```bash
# Profil complet (description, index, TER, réplication, holdings, allocations)
uv run skills/justetf/scripts/justetf_etfs.py details IE00B4L5Y983
uv run skills/justetf/scripts/justetf_etfs.py details IE00B4L5Y983 -o .tmp/etf-details.json
```

#### `generate` — Générer ou mettre à jour une fiche ETF

```bash
# Créer ou mettre à jour la fiche d'un ETF
uv run skills/justetf/scripts/justetf_etfs.py generate IE00B4L5Y983
```

Fetch les données justETF, génère la fiche complète depuis le template Jinja2 (`skills/write-etf/assets/etf-template.md.j2`). L'éligibilité PEA est lue depuis `docs/actifs/etf-eligibles-pea.md`.

#### `bulk-update` — Mettre à jour tous les ETFs

```bash
uv run skills/justetf/scripts/justetf_etfs.py bulk-update
# ou
make etfs
```

Met à jour toutes les fiches existantes dans `docs/actifs/etf/` en une seule requête API (overview). Utiliser `git diff` pour review des changements.

### Filtres disponibles pour `search`

| Filtre | Description | Valeurs |
|---|---|---|
| `--pea` | ETF éligibles PEA uniquement | flag |
| `--query` | Recherche texte (nom ou ISIN) | texte libre |
| `--asset-class` | Classe d'actifs | `equity`, `bonds`, `commodities`, etc. |
| `--region` | Région | `World`, `Europe`, `North America`, etc. |
| `--provider` | Émetteur | `Amundi`, `iShares`, `Xtrackers`, etc. |
| `--country` | Pays cible | code ISO alpha-2 |
| `--limit` | Nombre max de résultats | entier (défaut : tous) |

### Données retournées par `search`

Pour chaque ETF : `isin`, `name`, `ter`, `size`, `domicile`, `currency`, `replication`, `distribution`, `last_year`, `last_three_years`, `last_five_years`, `holdings`.

### Données retournées par `details`

Pour un ETF : `isin`, `name`, `description`, `index`, `ter`, `fund_size_eur`, `replication`, `distribution_policy`, `fund_currency`, `fund_domicile`, `inception_date`, `top_holdings`, `countries`, `sectors`, `volatility_1y`.

## Filtre PEA : fonctionnement technique

L'overview justETF n'a pas de colonne `pea`. Le filtre PEA est injecté dans les paramètres de requête via `&pea=true` ajouté à `etfParams` (monkey-patch de `make_etf_params`). C'est le même mécanisme que le screener web de justETF.

## Processus typique

1. **Mettre à jour toutes les fiches ETF** → `bulk-update` (ou `make etfs`)
2. **Créer/mettre à jour un ETF spécifique** → `generate <ISIN>`
3. **Explorer les données** → `search` et `details` pour consultation

## Sources

- [justETF — Screener](https://www.justetf.com/en/find-etf.html)
- [justETF — Screener PEA](https://www.justetf.com/en/find-etf.html?pea=true)
- Bibliothèque : [justetf-scraping](https://github.com/patjlm/justetf-scraping) (fork avec corrections)