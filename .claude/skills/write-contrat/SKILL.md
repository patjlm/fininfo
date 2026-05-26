---
name: write-contrat
description: >-
  Créer ou mettre à jour une fiche de contrat financier (PER, assurance vie,
  PEA, CTO, etc.). Combine les données du comparatif sinvestir.fr avec des
  recherches sur le site du distributeur pour documenter frais, supports,
  contraintes spécifiques et conditions. Utiliser quand l'utilisateur veut
  documenter un contrat spécifique.
allowed-tools: Read Write Edit WebFetch WebSearch Bash
---

# Créer / mettre à jour une fiche de contrat

## Données d'entrée

Le comparatif sinvestir.fr fournit la liste des contrats et des avis. Récupérer les données via le skill `fetch-comparisons` si nécessaire.

| Type de contrat | Fichier sinvestir | Dossier de sortie | Template |
|---|---|---|---|
| PER | `.tmp/per-data.json` | `docs/contrats/per/` | [contrat-template-per.md](assets/contrat-template-per.md) |
| Assurance vie | `.tmp/life-insurance-data.json` | `docs/contrats/assurance-vie/` | [contrat-template-av.md](assets/contrat-template-av.md) |
| PEA | `.tmp/pea-data.json` | `docs/contrats/pea/` | [contrat-template-pea.md](assets/contrat-template-pea.md) |
| CTO | `.tmp/cto-data.json` | `docs/contrats/cto/` | [contrat-template-cto.md](assets/contrat-template-cto.md) |

## Processus

1. **Lire les données sinvestir** pour le contrat concerné
2. **Rechercher UNIQUEMENT sur le site du distributeur** (et de l'assureur si pertinent) — ne JAMAIS utiliser de sites tiers (blogs, comparateurs, forums comme cleerly.fr, ideal-investisseur.fr, etc.) :
   - Page produit officielle
   - Conditions générales / notice d'information
   - Annexe des supports (liste et frais des UC, performances brutes vs nettes)
   - Grille tarifaire détaillée
   - Liste des supports (UC, ETF, SCPI)
3. **Vérifier les listes de supports** (ETF, SCPI, SCI, OPCI, fonds obligataires) :
   - Récupérer la liste complète depuis le site officiel du distributeur ou de l'assureur
   - Pour les contrats Linxea : utiliser le skill `fetch-linxea-funds` (API Morningstar)
   - Pour les autres contrats : utiliser le skill `fetch-support-lists` ou vérifier manuellement sur le site du distributeur
   - Comparer avec la liste existante dans la fiche : ajouter les nouveaux supports, retirer ceux qui n'apparaissent plus
   - Chaque support doit avoir son ISIN quand disponible
   - Pour les ETF : créer un lien `[ISIN](../../actifs/etf/<ISIN>.md)` si la fiche existe. Si elle n'existe pas, utiliser le skill `write-etf` pour la créer, puis ajouter le lien.
4. **Documenter les contraintes spécifiques** — c'est la valeur ajoutée :
   - Règles d'arbitrage (ex : « arbitrage du fonds euros vers SCPI interdit, versement uniquement »)
   - Limites d'investissement (ex : « 40 % SCPI maximum », « 25 % minimum en UC pour accéder au fonds euros boosté »)
   - Montants minimums par opération (versement initial, versements libres, arbitrage)
   - Conditions de la gestion pilotée (surcoûts, profils disponibles)
   - Conditions spécifiques au type (voir table ci-dessous)
   - Pénalités ou délais spécifiques
5. **Remplir les frais dans le frontmatter** — chaînes avec `%` et contexte si nécessaire :
   - PER / AV : `frais-versement`, `frais-gestion-uc`, `frais-arbitrage`
   - Format : `"X %"` ou `"X % (précision)"` si conditions multiples
   - Exemples : `frais-versement: "0 %"`, `frais-gestion-uc: "0,50 %"`, `frais-arbitrage: "0 % (0,10 % sur ETF)"`
6. **Rédiger la fiche** en suivant le template du type concerné
7. **Écrire le fichier** dans le dossier de sortie avec le slug généré

## Spécificités par type de contrat

### PER
- **Frontmatter `type`** : `contrat-per`
- **Frais spécifiques** : rente
- **Sections propres** : fonds euros, UC, transfert entrant/sortant
- **Fiscalité** : non (voir enveloppe `docs/enveloppes/per.md`)
- **Contraintes clés** : transfert entrant/sortant, gestion pilotée horizon retraite

### Assurance vie
- **Frontmatter `type`** : `contrat-assurance-vie`
- **Frais spécifiques** : rachat
- **Sections propres** : fonds euros, UC, fiscalité (avant/après 8 ans, transmission)
- **Contraintes clés** : rachat partiel, avance sur contrat, clause bénéficiaire

### PEA
- **Frontmatter `type`** : `contrat-pea`
- **Acteur** : courtier (pas d'assureur)
- **Frais spécifiques** : courtage (grille par palier), change
- **Sections propres** : produits/fonctionnalités, propriété/transfert, réglementation/IFU
- **Pas de sections** : fonds euros, UC (remplacées par Produits)
- **Fiscalité** : non (voir enveloppe `docs/enveloppes/pea.md`)
- **Contraintes clés** : marchés accessibles, DCA, fractions d'actions, IFU, domiciliation du compte

### CTO
- **Frontmatter `type`** : `contrat-cto`
- **Acteur** : courtier (pas d'assureur)
- **Frais spécifiques** : courtage par marché (actions FR, actions US, ETF EU), change
- **Sections propres** : produits/fonctionnalités (crypto, rémunération liquidités, CTO enfant), propriété/transfert
- **Pas de sections** : fonds euros, UC (remplacées par Produits)
- **Fiscalité** : non (voir enveloppe `docs/enveloppes/cto.md`)
- **Contraintes clés** : frais par marché (FR/US/ETF), crypto, fractions d'actions, DCA, rémunération liquidités, propriété des titres, domiciliation (FR/étranger → déclaration), IFU

## Règles

- Les contraintes spécifiques sont ESSENTIELLES : c'est ce qui différencie les fiches d'un simple copier-coller du comparatif
- Les points forts/faibles reprennent les `importantPoints` de sinvestir mais peuvent être enrichis
- Toujours lier vers la fiche enveloppe correspondante pour les règles générales
- Les règles de formatage, sources, slug et fiabilité sinvestir sont dans [AGENTS.md](../../AGENTS.md)