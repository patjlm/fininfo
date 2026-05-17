---
name: fetch-comparisons
description: >-
  Récupérer les données de comparaison de produits financiers (PER, PEA,
  assurance vie, SCPI, CTO, crypto, banque en ligne) depuis
  simulateurs.sinvestir.fr et générer/mettre à jour les fiches markdown
  correspondantes. Utiliser quand l'utilisateur veut importer ou rafraîchir
  les comparatifs de produits financiers.
allowed-tools: Read Write Edit Bash
---

# Récupérer et mettre à jour les comparatifs de produits financiers

## Prérequis

Un fichier `cookie.json` contenant les cookies d'authentification de
`simulateurs.sinvestir.fr` doit exister à la racine du projet.

### Vérification

1. Vérifier que `cookie.json` existe à la racine du workspace
2. Si absent, demander à l'utilisateur :
   > cookie.json est absent. Pour le créer :
   > 1. Se connecter à https://simulateurs.sinvestir.fr/les-comparateurs
   > 2. Exporter les cookies avec une extension navigateur (Cookie Quick Manager, EditThisCookie, etc.)
   > 3. Sauvegarder le fichier JSON exporté sous `cookie.json` à la racine du projet
3. Ne PAS continuer sans ce fichier

## Types de comparaison disponibles

| Type API | Catégorie | Dossier docs |
|---|---|---|
| `per` | Plan Épargne Retraite | `docs/contrats/per/` |
| `pea` | Plan Épargne Actions | `docs/contrats/pea/` |
| `life-insurance` | Assurance Vie | `docs/contrats/assurance-vie/` |
| `scpi` | SCPI | `docs/contrats/scpi/` |
| `cto` | Compte-Titres | `docs/contrats/cto/` |
| `crypto` | Crypto | `docs/contrats/crypto/` |
| `online-bank` | Banque en ligne | `docs/contrats/banque-en-ligne/` |
| `online-bank-pro` | Banque en ligne pro | `docs/contrats/banque-en-ligne-pro/` |

## Processus

1. Vérifier `cookie.json` (voir Prérequis)
2. Récupérer les données :
   ```bash
   uv run .claude/skills/fetch-comparisons/scripts/fetch-sinvestir.py <type> -o .tmp/<type>-data.json
   ```
3. Lire le JSON obtenu
4. Déléguer la rédaction des fiches au skill `write-contrat`
5. Mettre à jour la fiche enveloppe dans `docs/enveloppes/` avec les liens vers les contrats

### Structure des données API

Chaque entrée contient un champ `data` avec les sections :

- `general` : distributeur, assureur, type de plan, gestion, versement minimum
- `fees` : frais de versement, gestion UC, gestion fonds euros, arbitrage, rente
- `euroFunds` : fonds disponibles, performances, contraintes
- `unitLinked` : nombre d'UC, ETF, SCPI, titres vifs, rééquilibrage
- `customerExperience` : avis clients, contact, app mobile, ergonomie
- `globalNote` : note globale, points importants, services complémentaires

## Règles

- Appliquer les [conventions communes](../../AGENTS.md) (formatage, sources, dates)
- Source : `simulateurs.sinvestir.fr` (toujours citer)
- Si une donnée vaut `/` ou est vide, écrire « Non disponible »
- Utiliser la date du jour pour toutes les sections lors d'une mise à jour
- Garder les notes sur 5 (pas sur 10)

## Mise à jour d'une fiche existante

1. Lire la fiche existante
2. Comparer avec les nouvelles données
3. Ne modifier QUE les sections dont les données ont changé
4. Mettre à jour `<!-- Mis à jour -->` des sections modifiées
5. Mettre à jour `derniere-verification` dans le frontmatter
