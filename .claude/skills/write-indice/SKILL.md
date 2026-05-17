---
name: write-indice
description: >-
  Créer ou mettre à jour une fiche d'indice boursier dans docs/actifs/indices/<slug>.md.
  Récupère les données depuis le site officiel du fournisseur (MSCI, S&P, STOXX,
  FTSE Russell, Nasdaq) pour documenter caractéristiques, composition et performances.
  Utiliser quand l'utilisateur veut documenter un indice spécifique.
allowed-tools: Read Write Edit Bash WebFetch WebSearch
---

# Créer / mettre à jour une fiche d'indice boursier

## Données d'entrée

Le nom de l'indice à documenter.

## Processus

1. **Identifier le fournisseur** et trouver la factsheet officielle :
   - MSCI : `www.msci.com/documents/10199/...` (factsheets PDF) ou `www.msci.com/our-solutions/indexes/...`
   - S&P Dow Jones Indices : `www.spglobal.com/spdji/en/indices/<slug>/`
   - STOXX : `www.stoxx.com/index-details?symbol=<ticker>`
   - FTSE Russell : `www.ftserussell.com/products/indices/<slug>`
   - Nasdaq : `www.nasdaq.com/market-activity/index/<ticker>`
2. **Récupérer les données officielles** depuis la factsheet :
   - Nom complet officiel
   - Date de lancement
   - Nombre de constituants
   - Zone géographique couverte (nombre de pays, liste)
   - Critères d'inclusion (capitalisation minimale, liquidité, flottant)
   - Méthode de pondération
   - Fréquence de rebalancement
   - Devise de référence
3. **Récupérer la composition** :
   - Répartition géographique (top pays)
   - Répartition sectorielle (GICS)
   - Top 10 constituants avec poids
4. **Récupérer les performances** :
   - Performances annualisées (1, 3, 5, 10 ans)
   - Version gross return ou net return (préciser)
5. **Identifier les ETF qui répliquent cet indice** :
   ```bash
   grep -rli '<nom-indice>' docs/actifs/etf/
   ```
6. **Lister les variantes connues** (ESG, SRI, hedged, small cap, etc.)
7. **Rédiger la fiche** en suivant le template [indice-template.md](assets/indice-template.md)
8. **Écrire le fichier** dans `docs/actifs/indices/<slug>.md`

## Hiérarchie des sources

1. **Site officiel du fournisseur** (factsheet, méthodologie, page produit) — source primaire
2. **Fiches ETF existantes** dans le wiki — pour la section « ETF répliquant cet indice »

## Règles

- **Slug** : kebab-case du nom courant, sans accents (ex : « MSCI World » → `msci-world`, « S&P 500 » → `sp-500`, « EURO STOXX 50 » → `euro-stoxx-50`)
- **Nombre de constituants** : nombre dans le frontmatter (`nombre-de-constituants: 1400`), pas de chaîne
- **Noms de secteurs en français** : toujours utiliser les noms GICS traduits :
  - Information Technology → Technologies de l'information
  - Financials → Finance
  - Industrials → Industrie
  - Consumer Discretionary → Consommation discrétionnaire
  - Communication Services → Services de communication
  - Health Care → Santé
  - Consumer Staples → Consommation de base
  - Energy → Énergie
  - Materials → Matériaux
  - Utilities → Services aux collectivités
  - Real Estate → Immobilier
- **Valeurs précises** : ne pas utiliser `~X %` ni `X-Y %`. Si la source donne une valeur, l'écrire telle quelle. Si elle est indisponible, écrire « Non communiqué »
- **Données manquantes** : écrire « Non communiqué » si indisponible. Utiliser `[à vérifier]` uniquement si une valeur est fournie mais incertaine — pas pour des valeurs manquantes
- **Ne PAS inventer de données** : si la factsheet ne fournit pas un champ, marquer « Non communiqué ». Ne pas estimer des poids à partir de sources secondaires (ETF proxy) sans le mentionner
- **Top 10 constituants** : préférer les poids officiels de la factsheet. Si indisponibles, lister les noms sans poids (`Non communiqué`) plutôt que de mélanger des sources incohérentes
- **Performances** : préciser si gross return, net return ou price return
- **Section « ETF répliquant cet indice »** : lister les ETF documentés dans le wiki avec lien relatif
- **Section « Variantes »** : mentionner les variantes principales sans créer de fiche séparée (sauf demande explicite)
- Les règles de formatage, sources et langue sont dans [AGENTS.md](../../AGENTS.md)

## Mise à jour d'une fiche existante

1. Lire la fiche existante
2. Ne modifier QUE les sections concernées
3. Mettre à jour `<!-- Mis à jour -->` des sections modifiées
4. Mettre à jour `derniere-verification` dans le frontmatter
