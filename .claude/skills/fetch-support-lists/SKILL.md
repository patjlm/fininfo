---
name: fetch-support-lists
description: >-
  Récupérer la liste exhaustive des supports (ETF, SCPI, SCI, OPCI, OPCVM)
  disponibles sur un contrat PER, assurance vie ou PEA depuis le site du
  distributeur. Ajouter les listes avec ISIN et contraintes spécifiques dans
  la fiche markdown du contrat. Utiliser quand l'utilisateur veut documenter
  les supports d'un contrat financier.
allowed-tools: Read Write Edit WebFetch WebSearch
compatibility: Requires WebFetch permissions for financial domains (configured in .claude/settings.local.json)
---

# Récupérer les listes de supports d'un contrat

## Objectif

Ajouter les listes exhaustives de supports (ETF, SCPI, SCI, OPCI, OPCVM, fonds obligataires)
dans la fiche markdown d'un contrat, avec ISIN, nom, et contraintes spécifiques.

## Processus

1. **Lire la fiche existante** du contrat dans `docs/contrats/<categorie>/<slug>.md`
2. **Identifier la source** : URL de la liste des supports sur le site du distributeur
3. **Récupérer les données** via WebFetch sur la page du distributeur
4. **Stratégie de fallback** si WebFetch échoue (SPA, page dynamique) :
   - Essayer WebSearch pour trouver des articles listant les supports avec ISIN
   - Chercher des PDF de notices d'information / annexes financières du contrat
   - Essayer des sources tierces fiables (Quantalys, francetransactions.com, moneyvox.fr)
5. **Formater et insérer** les tables dans le fichier markdown
6. **Vérifier** que chaque ETF a un ISIN — ne JAMAIS inventer un ISIN

## Format des sections à ajouter

Insérer ces sections **avant** `## Expérience client` (ou `## Avis synthétique` si absent).

### Pour les contrats en gestion libre

```markdown
## Liste des ETF disponibles
<!-- Mis à jour : YYYY-MM-DD -->
<!-- Source : URL_DE_LA_PAGE_DU_DISTRIBUTEUR -->

| Nom | ISIN | Catégorie | Frais spécifiques |
|---|---|---|---|
| Amundi MSCI World UCITS ETF | LU1681043599 | Actions Monde | 0,10 %/an |

## Liste des SCPI / SCI / OPCI disponibles
<!-- Mis à jour : YYYY-MM-DD -->
<!-- Source : URL_DE_LA_PAGE_DU_DISTRIBUTEUR -->

| Nom | Type | Contraintes spécifiques |
|---|---|---|
| Corum Origin | SCPI | 50 000 EUR max, pénalité 3 % < 3 ans, 85 % loyers |
```

### Pour les contrats en gestion pilotée uniquement

```markdown
## Supports utilisés en gestion pilotée
<!-- Mis à jour : YYYY-MM-DD -->
<!-- Source : URL_DE_LA_PAGE_DU_DISTRIBUTEUR -->

> Gestion pilotée uniquement — l'épargnant ne choisit pas individuellement les supports.

| Nom | ISIN | Type | Catégorie |
|---|---|---|---|
| Amundi MSCI World UCITS ETF | LU1681043599 | ETF | Actions Monde |
```

## Règles impératives

- Appliquer les [conventions communes](../../AGENTS.md) (sources, formatage, dates)
- **ISIN obligatoire** pour chaque ETF / OPCVM — c'est l'identifiant unique
- **Ne JAMAIS inventer un ISIN** — si introuvable, écrire `[ISIN à compléter]`
- **Commentaire `<!-- Source : URL -->`** : ESSENTIEL pour les futures mises à jour — doit pointer vers la page officielle du distributeur/assureur
- **Si liste incomplète** : noter `[liste partielle — X supports sur Y identifiés]` en tête de table
- **Contraintes SCPI** : toujours documenter les règles spécifiques au contrat (% max, pénalités, redistribution loyers, plafond EUR, arbitrage interdit, etc.)

## URLs des listes de supports par contrat PER

| Contrat | URL ETF | URL SCPI/immo |
|---|---|---|
| Linxea Spirit PER | https://www.linxea.com/retraite/linxea-spirit-per/supports-disponibles-sur-linxea-spirit-per/trackers-etf/ | https://www.linxea.com/assurance-vie/linxea-spirit-2/supports-disponibles-sur-linxea-spirit-2/support-fond-immo/ |
| Linxea Suravenir | https://www.linxea.com/retraite/suravenir-per/supports-disponibles-sur-suravenir-per/trackers-etf/ | https://www.linxea.com/retraite/suravenir-per/supports-disponibles-sur-suravenir-per/fonds-immobiliers-suravenir-per/ |
| meilleurtaux Liberté | https://placement.meilleurtaux.com/retraite/per/meilleur-per/meilleurtaux-liberte-per.html | (même page) |
| Placement-direct | https://www.placement-direct.fr/retraite/per-placement-direct/allocation-libre | (même page) |
| Fortuneo | https://www.fortuneo.fr/per-plan-epargne-retraite/gestion-libre | https://www.fortuneo.fr/assurance-vie/scpi-immobilier |
| MIF Retraite | https://www.mifassur.com/retraite/mif-per-retraite-gestion-libre | (même page) |
| Lucya Abeille | https://www.assurancevie.com/asv/nos-contrats/lucya-abeille-per/liste-supports | (même page, pas de SCPI) |
| MATLA | https://s.brsimg.com/content/pdf/matla/boursorama-an-financiere.pdf | (recherche web) |
| BNP Paribas | https://www.quantalys.com/Contrat/Supports/2270?bISR=True | (pas de SCPI) |
| Caravel | https://airtable.com/appB7xvLa5K0wrzQa/shryiVGvWhWK5RidA | https://airtable.com/appB7xvLa5K0wrzQa/shrxmCKOMwwgxDUOg |
| Corum PERLife | https://www.corum.fr/per/corum-perlife/placements | (même page, pas d'ETF) |
| Goodvest | https://www.goodvest.fr/ (pilotée) | (pas de SCPI) |
| Nalo | https://www.nalo.fr/ (pilotée) | (pas de SCPI) |
| Yomoni Retraite | https://www.yomoni.fr/legal/supports-investissement | (pas de SCPI) |
| Yomoni Retraite+ | https://www.yomoni.fr/legal/supports-investissement | (pas de SCPI) |
| Individuel Carac | https://www.carac.fr/information-precontractuelle#per | (pas de SCPI) |
