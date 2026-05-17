---
name: write-scpi
description: >-
  Créer ou mettre à jour une fiche SCPI dans docs/actifs/scpi/<slug>.md.
  Combine les données sinvestir.fr (comparatif, avis subjectifs) avec le site
  officiel de la société de gestion pour documenter caractéristiques, frais,
  performances, patrimoine et modalités de détention.
  Utiliser quand l'utilisateur veut documenter une SCPI spécifique.
allowed-tools: Read Write Edit Bash WebFetch WebSearch
---

# Créer / mettre à jour une fiche SCPI

## Données d'entrée

Le nom de la SCPI à documenter. Les données sinvestir sont dans `.tmp/scpi-data.json` (généré par le skill `fetch-comparisons` avec le type `scpi`).

## Processus

1. **Extraire les données sinvestir** depuis `.tmp/scpi-data.json` (chercher par nom)
2. **Identifier la société de gestion** et trouver le site officiel :
   - ALDERAN : `www.alderan.fr`
   - ARKEA REIM : `www.arkea-reim.fr`
   - ATLAND VOISIN : `www.epargnepierre.com` ou `www.atland-voisin.com`
   - CORUM L'ÉPARGNE : `www.corum.fr`
   - EPSILON CAPITAL : `www.epsicap.fr`
   - IROKO : `www.iroko.eu`
   - NOVAXIA INVESTISSEMENT : `www.novaxia-investissement.fr`
   - REMAKE AM : `www.remake-am.fr`
   - SOFIDY : `www.sofidy.com`
   - SOGENIAL IMMOBILIER : `www.sogenial.fr`
   - ADVENIS REIM : `www.advenis-reim.com`
   - WEMO REIM : `www.wemo-reim.com`
   - Autres : rechercher `site:<domaine-societe-de-gestion> <nom SCPI>`
3. **Récupérer et vérifier les données sur le site officiel** :
   - Prix de souscription, valeur de retrait, valeur de reconstitution (confirmer vs sinvestir)
   - Frais détaillés (souscription, gestion, acquisition, cession, travaux)
   - Taux de distribution historique (confirmer)
   - TOF, WALB, taux d'endettement
   - Répartition géographique et sectorielle (confirmer vs sinvestir)
   - ISIN (souvent dans le DIC ou le bulletin trimestriel)
   - Date de création, nombre d'associés, capitalisation
   - TRI 5 ans / 10 ans (si disponible dans le rapport annuel)
4. **Identifier les contrats qui référencent cette SCPI** :
   ```bash
   grep -rli '<nom-scpi>\|<isin>' docs/contrats/
   ```
5. **Rédiger la fiche** en suivant le template [scpi-template.md](assets/scpi-template.md)
6. **Écrire le fichier** dans `docs/actifs/scpi/<slug>.md`

## Hiérarchie des sources

1. **Site officiel de la société de gestion** (DIC, bulletin trimestriel, rapport annuel) — source primaire pour toutes les données objectives
2. **AMF GECO** (`geco.amf-france.org`) — ISIN, agrément
3. **sinvestir.fr** (`.tmp/scpi-data.json`) — avis subjectifs (note, points clés), données objectives à cross-checker
4. **primaliance.com** — agrégateur professionnel, utile pour cross-check

## Règles

- **Frontmatter numérique** : `prix-de-part: 610` (nombre, pas `"610 EUR"`), `taux-de-distribution: 5.49` (nombre avec point décimal, pas `"5,49%"`)
- **Slug** : kebab-case du nom, sans accents (ex : « Corum Origin » → `corum-origin`, « Épargne Pierre Europe » → `epargne-pierre-europe`)
- **Données objectives** (frais, prix, performances) : TOUJOURS vérifier sur le site de la société de gestion. Ne pas reprendre sinvestir sans vérification
- **Données subjectives** (note, avis, points clés sinvestir) : inclure dans la section « Avis et comparatifs (subjectif) » en citant la source
- **Section « Contrats référençant cette SCPI »** : lister tous les contrats trouvés avec lien relatif
- **Section « Avis et comparatifs »** : toujours inclure les liens vers avenuedesinvestisseurs.fr :
  - `https://avenuedesinvestisseurs.fr/investissement-immobilier/scpi-societes-civiles-de-placement-immobilier/`
  - `https://avenuedesinvestisseurs.fr/meilleure-assurance-vie-scpi-comparatif/`
- **Données manquantes** : écrire « Non communiqué » si indisponible, ajouter `[à vérifier]` si incertaine
- **Ne PAS inventer de données** : si la société de gestion et sinvestir ne fournissent pas un champ, marquer « Non communiqué »
- Les règles de formatage, sources et langue sont dans [AGENTS.md](../../AGENTS.md)

## Mise à jour d'une fiche existante

1. Lire la fiche existante
2. Ne modifier QUE les sections concernées
3. Mettre à jour `<!-- Mis à jour -->` des sections modifiées
4. Mettre à jour `derniere-verification` dans le frontmatter
