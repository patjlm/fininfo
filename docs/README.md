# Fininfo — Documentation

<!-- Mis à jour : 2026-05-17 -->

Wiki des produits financiers français. Sources officielles uniquement.

## Structure

Chaque fiche a un frontmatter YAML avec `type`, `slug`, `derniere-verification`. Les champs numériques (frais, TER, prix) sont des nombres, pas des chaînes — utilisables pour filtrer et comparer sans lire le corps du document.

### Enveloppes (`enveloppes/`)

11 fiches des cadres réglementaires (Livret A, PEA, assurance vie, PER, CTO, SCPI en direct, etc.).
Frontmatter : `nom`, `type: enveloppe`, `slug`.

- [README enveloppes](enveloppes/README.md) — tableau comparatif plafonds et fiscalité

### Contrats (`contrats/`)

72 fiches de contrats par catégorie. Frontmatter : `nom`, `type`, `slug`, `distributeur`/`courtier`, `assureur`, frais numériques (`frais-versement`, `frais-gestion-uc`, `frais-arbitrage`).

- [PER](contrats/per/README.md) — 16 contrats PER individuels
- [Assurance vie](contrats/assurance-vie/README.md) — 21 contrats d'assurance vie
- [PEA](contrats/pea/README.md) — 17 courtiers PEA
- [CTO](contrats/cto/README.md) — 18 courtiers compte-titres

### Actifs (`actifs/`)

630 fiches d'actifs financiers. Les ETF sont identifiés par ISIN.

- [README actifs](actifs/README.md) — sous-catégories et comptages
- **ETF** (`actifs/etf/`) — 604 fiches. Frontmatter : `isin`, `ticker`, `emetteur`, `indice`, `ter` (nombre), `eligibilite-pea`
- **SCPI** (`actifs/scpi/`) — 20 fiches. Frontmatter : `societe-de-gestion`, `categorie`, `prix-de-part` (nombre), `taux-de-distribution` (nombre)
- **OPCVM** (`actifs/opcvm/`) — 5 fiches
- **SC** (`actifs/sc/`) — 1 fiche
- [ETF éligibles PEA](actifs/etf-eligibles-pea.md) — liste filtrée par émetteur

### Institutions (`institutions/`)

Fiches des banques, courtiers et assureurs _(à venir)_.

- [README institutions](institutions/README.md)

## Requêtes courantes

- **Comparer les frais PER** → lire `contrats/per/README.md` (tableau généré depuis le frontmatter)
- **ETF éligibles PEA** → lire `actifs/etf-eligibles-pea.md` ou filtrer `eligibilite-pea: oui` dans le frontmatter des fichiers `actifs/etf/`
- **Quel contrat propose un ETF donné ?** → chercher l'ISIN dans les fiches contrats, ou lire la section « Contrats référençant cet ETF » dans la fiche ETF
- **Règles d'une enveloppe** → lire la fiche dans `enveloppes/` (fiscalité, plafonds, conditions)

## Fiabilité des données

- Les fiches sont générées par des agents IA à partir de sources officielles (sites des sociétés de gestion, assureurs, distributeurs, AMF) et cross-vérifiées avec des comparateurs (Primaliance, MeilleureSCPI, sinvestir.fr)
- Les données marquées `[à vérifier]` n'ont pas pu être confirmées sur la source primaire — ne pas s'y fier sans vérification manuelle
- Les données marquées `Non communiqué` n'ont pas été trouvées dans les sources consultées
- Les performances passées ne préjugent pas des performances futures
- Ce wiki n'est pas un conseil en investissement — consulter un conseiller financier avant toute décision
- Date de dernière vérification indiquée dans le frontmatter — les données peuvent devenir obsolètes
