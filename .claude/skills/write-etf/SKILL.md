---
name: write-etf
description: >-
  Créer ou mettre à jour une fiche ETF dans docs/actifs/etf/<isin>.md.
  Combine les données justETF (skill justetf) avec le site officiel de
  l'émetteur pour documenter profil, allocations, performances et risques.
  Utiliser quand l'utilisateur veut documenter un ETF spécifique.
allowed-tools: Read Write Edit Bash WebFetch WebSearch
---

# Créer / mettre à jour une fiche ETF

## Données d'entrée

L'ISIN de l'ETF à documenter. Les données sont récupérées via le skill `justetf` puis vérifiées sur le site de l'émetteur.

## Processus

1. **Récupérer les données justETF** via le script du skill `justetf` :
   ```bash
   uv run .claude/skills/justetf/scripts/justetf_etfs.py details <ISIN>
   ```
2. **Identifier l'émetteur** et rechercher la page produit officielle :
   - Amundi : `www.amundietf.fr/fr/professionnels/produits/equity/<isin>`
   - iShares/BlackRock : `www.ishares.com/fr/investisseur-prive/fr/produits/<slug>`
   - BNP Paribas Easy : `www.bnpparibas-am.com/fr-fr/particulier/fundsheet/etf/<isin>`
   - Xtrackers/DWS : `etf.dws.com/fr-fr/<slug>`
   - Vanguard : `www.fr.vanguard/professionnel/produits/<slug>`
   - Autres : rechercher `site:<domaine-emetteur> <ISIN>`
3. **Vérifier et compléter** les données justETF avec le site de l'émetteur :
   - Description officielle de l'ETF
   - Indice de référence exact (nom complet)
   - TER (confirmer)
   - Tracking error (souvent absent de justETF)
   - Méthode de réplication détaillée
   - Date de création
4. **Identifier les contrats qui référencent cet ISIN** :
   ```bash
   grep -rl '<ISIN>' docs/contrats/ docs/actifs/
   ```
5. **Rédiger la fiche** en suivant le template [etf-template.md](assets/etf-template.md)
6. **Écrire le fichier** dans `docs/actifs/etf/<ISIN>.md`

## Règles

- **TER numérique** : `ter: 0.25` (nombre, pas `"0.25%"`)
- **Réplication en français** : `Physique`, `Échantillonnage`, `Synthétique`, `Adossé` (pour ETC matières premières). Commentaire YAML si précision utile : `replication: Adossé  # or physique`
- **Distribution en français** : `Capitalisation`, `Distribution`
- **Slug = ISIN** : le nom du fichier est toujours `<ISIN>.md` (ex : `IE00B4L5Y983.md`)
- **Section « Contrats référençant cet ETF »** : lister tous les contrats qui mentionnent cet ISIN avec lien relatif
- **Tracking error** : inclure si disponible sur le site de l'émetteur, sinon écrire « Non communiqué »
- **Données manquantes** : écrire « Non communiqué » si indisponible, ajouter `[à vérifier]` si incertaine
- **Performances** : utiliser les données justETF (champs `last_year`, `last_three_years`, `last_five_years`)
- **Allocations** : top 10 holdings, répartition géographique et sectorielle depuis justETF
- **Ne PAS inventer de données** : si justETF ne retourne pas un champ et que le site émetteur ne le fournit pas, marquer « Non communiqué »
- Les règles de formatage, sources et langue sont dans [AGENTS.md](../../AGENTS.md)

## Mise à jour d'une fiche existante

1. Lire la fiche existante
2. Ne modifier QUE les sections concernées
3. Mettre à jour `<!-- Mis à jour -->` des sections modifiées
4. Mettre à jour `derniere-verification` dans le frontmatter