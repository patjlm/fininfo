---
name: fetch-linxea-funds
description: >-
  Récupérer la liste complète des supports (ETF, OPCVM, SCPI, SCI, OPCI)
  disponibles sur un contrat Linxea via l'API Morningstar. Chaque contrat
  a un universe ID dédié qui retourne exactement les fonds éligibles.
  Utiliser pour obtenir les listes exhaustives avec ISIN pour les contrats
  Linxea Spirit PER, Linxea Suravenir PER, etc.
allowed-tools: Read Write Edit Bash WebFetch
compatibility: Requires Python 3 and network access to login-prod.morningstar.com and www.us-api.morningstar.com
---

# Récupérer les fonds Linxea via l'API Morningstar

## Contrats et Universe IDs

Chaque contrat Linxea a son propre univers Morningstar :

| Contrat | Universe ID | Pertinent pour |
|---|---|---|
| **Linxea Spirit PER** | `FEEUR$$ALL_5650` | `docs/contrats/per/linxea-spirit-per.md` |
| **Linxea Suravenir PER** | `FEEUR$$ALL_5649` | `docs/contrats/per/linxea-suravenir.md` |
| Linxea Spirit 2 (AV) | `FEEUR$$ALL_5627` | futur |
| Linxea PER | `FEEUR$$ALL_5252` | futur |
| Linxea Avenir 2 (AV) | `FEEUR$$ALL_7170` | futur |
| Linxea Avenir (AV) | `FEEUR$$ALL_1016` | futur |
| Linxea Vie (AV) | `FEEUR$$ALL_842` | futur |
| Linxea Zen (AV) | `FEEUR$$ALL_2659` | futur |

## Processus

1. Lancer le script pour récupérer les fonds :
   ```bash
   python3 skills/fetch-linxea-funds/scripts/fetch_morningstar.py <universe_id> -o .tmp/linxea-<contrat>.json
   ```
2. Le script obtient automatiquement un bearer token (OAuth2, credentials publics Linxea)
3. Il requête l'API Morningstar screener avec l'universe ID
4. Il retourne la liste complète en JSON (ISIN, nom, catégorie, frais, performances, etc.)
5. Mettre à jour la fiche contrat avec les données

## SCPI / SCI / OPCI

Les supports immobiliers ne sont **PAS** dans le screener Morningstar.
Pour Spirit 2 et Spirit PER, ils sont disponibles via l'API WordPress Linxea :
```
https://www.linxea.com/wp-json/wp/v2/scpi?per_page=100&contract=spirit-per
```

## Données retournées par l'API

Pour chaque fonds :
- `isin` : code ISIN (identifiant unique)
- `name` : nom complet
- `categoryName` : catégorie Morningstar
- `starRatingM255` : note Morningstar (1-5 étoiles)
- `srlessSRRI` : SRRI (1-7)
- `ongoingCharge` : frais courants (%)
- `initialPurchaseFee` : frais d'entrée (%)
- `performanceFee` : commission de surperformance
- `returnM0` à `returnM120` : performances 1 mois à 10 ans
- `fundTNAV` : taille du fonds
- `SFDRClassification` : article SFDR (6, 8, 9)

## Contrats non-Linxea (même assureur)

meilleurtaux Liberté PER et Linxea Spirit PER partagent le même assureur (Spirica).
Les listes de supports sont très proches mais pas identiques — ne pas copier directement.

## Format de sortie pour les fiches

Voir le skill [fetch-support-lists](../fetch-support-lists/SKILL.md) pour le format des tables markdown.
