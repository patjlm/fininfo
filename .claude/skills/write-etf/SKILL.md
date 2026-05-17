---
name: write-etf
description: >-
  Générer ou mettre à jour une fiche ETF dans docs/actifs/etf/<isin>.md.
  Les fiches sont 100% générées depuis un template Jinja2 et les données
  justETF. Utiliser quand l'utilisateur veut documenter un ETF spécifique.
allowed-tools: Read Write Edit Bash
---

# Générer / mettre à jour une fiche ETF

## Commandes

### Un seul ETF

```bash
uv run skills/justetf/scripts/justetf_etfs.py generate <ISIN>
```

Fetch les données justETF (profile + overview), génère la fiche complète depuis le template Jinja2.

### Tous les ETFs existants

```bash
uv run skills/justetf/scripts/justetf_etfs.py bulk-update
# ou
make etfs
```

Met à jour toutes les fiches existantes en une seule requête API.

## Fonctionnement

1. **Données justETF** : le script fetch le profil (nom, émetteur, indice, TER, réplication, distribution, devise, domicile)
2. **Éligibilité PEA** : lue depuis `docs/actifs/etf-eligibles-pea.md` (pas d'appel API)
3. **Contrats référençant l'ETF** : grep automatique dans `docs/contrats/`
4. **Lien vers fiche indice** : matching automatique avec `docs/actifs/indices/`
5. **Génération** : template Jinja2 (`assets/etf-template.md.j2`) produit 100% du fichier (frontmatter + corps)

## Template

Le template est dans `assets/etf-template.md.j2`. Il produit :
- Frontmatter YAML (identité de l'ETF)
- Section Caractéristiques (bullet points)
- Section Contrats référençant cet ETF (si applicable)
- Section Sources (lien justETF)

Les données dynamiques (allocations, performances, holdings) ne sont pas dans les fiches — elles se requêtent à la volée via `justetf_etfs.py details <ISIN>`.

## Règles

- **Slug = ISIN** : le nom du fichier est toujours `<ISIN>.md`
- **TER numérique** : `ter: 0.25` dans le frontmatter
- **Réplication en français** : `Physique`, `Échantillonnage`, `Synthétique`, `Adossé`
- **Distribution en français** : `Capitalisation`, `Distribution`
- **SRI** : champ optionnel (indicateur de risque 1-7)
- Les règles de formatage, sources et langue sont dans [AGENTS.md](../../AGENTS.md)
