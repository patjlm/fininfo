# Fininfo — Wiki des produits financiers français

## Objectif

Wiki markdown de produits financiers français : enveloppes d'investissement, contrats, actifs. Toutes les données proviennent de sources officielles.

## Structure

- `docs/enveloppes/` — fiches des enveloppes (Livret A, PEA, AV, PER, etc.)
- `docs/contrats/` — fiches des contrats/produits par catégorie (`per/`, `pea/`, `assurance-vie/`, etc.)
- `docs/actifs/` — fiches des actifs (indices, ETF, SCPI, etc.)
- `skills/` — skills AI ([spec agentskills.io](https://agentskills.io/specification)) pour créer/mettre à jour les fiches

## Règles

- **Format** : bullet points concis, jamais de longs paragraphes
- **Sources** : toujours citer les URLs officielles (service-public.fr, economie.gouv.fr, amf-france.org, legifrance.gouv.fr, banque-france.fr)
- **Listes de supports** : UNIQUEMENT depuis le site du distributeur ou de l'assureur. Ne JAMAIS utiliser de sites tiers (blogs, comparateurs, forums) comme source — ils peuvent être obsolètes ou incorrects
- **Dates** : chaque section mentionne sa date de dernière mise à jour (`<!-- Mis à jour : YYYY-MM-DD -->`)
- **Homogénéité** : suivre le template du skill correspondant
- **Liens** : créer des liens entre documents quand pertinent
- **Langue** : contenu en français avec accents (é, è, ê, à, ç, etc.), identifiants techniques en kebab-case sans accents
- **Données manquantes** : écrire « Non communiqué » si indisponible, ajouter `[à vérifier]` si incertaine
- **Auto-maintenance** : quand une nouvelle règle ou convention est décidée, mettre à jour immédiatement ce fichier (AGENTS.md) et/ou le skill concerné. Garder ces fichiers concis et à jour — ils sont la source de vérité pour le comportement des agents

## Frontmatter

Chaque fiche a un frontmatter YAML validé par `make check`. Les schemas sont définis dans `.claude/skills/*/assets/schema-*.yaml`.

### Champ `derniere-verification`

- **Signification** : date à laquelle les données de la fiche ont été vérifiées comme encore exactes
- Mettre à jour à chaque vérification, même si rien n'a changé dans le contenu
- L'historique git montre quand le contenu a réellement changé

### Valeurs numériques

Les champs d'actifs (indices, ETF, SCPI) sont des **nombres** dans le frontmatter :

- `ter: 0.25` (pas `"0.25%"`)
- `prix-de-part: 610` (pas `"610 EUR"`)
- `taux-de-distribution: 5.49` (pas `"5,49%"`)
- `nombre-de-constituants: 1400` (pas `"~1400"`)

### Frais des contrats (chaînes)

Les frais des contrats (PER, AV) sont des **chaînes** avec `%` et contexte si nécessaire :

- `frais-versement: "0 %"`
- `frais-gestion-uc: "0,50 %"`
- `frais-arbitrage: "0 % (0,10 % sur ETF)"` — quand les frais varient selon le support

### Validation

Les schemas `.claude/skills/*/assets/schema-*.yaml` définissent pour chaque type :

- **required** : `true` (obligatoire) ou `false` (optionnel, sera requis à terme)
- **type** : `string`, `number`, `date`, `enum`
- **values** (pour `enum`) : liste des valeurs autorisées

Les champs optionnels (`required: false`) sont remplis par les skills lors de la création ou mise à jour des fiches. Les fichiers existants sans ces champs passent la validation.

## Validation

`make check` vérifie les liens internes, le frontmatter et les README avant commit :

- **Liens** : tous les liens markdown internes pointent vers des fichiers existants
- **Frontmatter** : champs obligatoires présents, types corrects, valeurs enum autorisées, format de date, cohérence slug/nom de fichier
- **README** : les tableaux comparatifs générés sont à jour (`make check-readmes`)

Aussi exécuté en CI via GitHub Actions sur chaque push/PR touchant `docs/`.

## README générés

Les README.md des sous-dossiers contiennent des tableaux comparatifs **générés automatiquement** depuis le frontmatter des fiches.

- `make readmes` — régénère tous les tableaux
- `make check-readmes` — vérifie que les tableaux sont à jour (CI)
- Les tableaux sont délimités par `<!-- BEGIN GENERATED -->` / `<!-- END GENERATED -->`
- Ne pas modifier le contenu entre ces marqueurs manuellement — il sera écrasé
- Le contenu hors marqueurs (titres, texte, règles) est préservé

Après avoir créé ou modifié une fiche, exécuter `make readmes` pour mettre à jour les tableaux.

## Conventions pour les fiches contrats

Ces conventions s'appliquent à tous les skills qui créent ou mettent à jour des fiches de contrats (`write-contrat`, `fetch-comparisons`, `fetch-support-lists`, etc.).

### Fiabilité des données sinvestir

- **Données subjectives** (notes, avis, points forts/faibles, appréciations) : utilisables telles quelles, en citant sinvestir comme source
- **Données objectives** (frais, performances, nombre de supports, conditions, contraintes) : DOIVENT être vérifiées et sourcées depuis le site officiel du distributeur ou de l'assureur. Ne pas reprendre les chiffres sinvestir sans vérification
- **`importantPoints`** (texte libre) : peut contenir des chiffres obsolètes même quand les champs structurés sont à jour — ne pas reprendre tel quel, utiliser uniquement comme point de départ
- **Assureur/distributeur** : peuvent être confondus ou inversés dans sinvestir — toujours vérifier sur le site officiel avant d'utiliser ces valeurs
- **Modes de gestion** : sinvestir peut indiquer "Gestion libre & pilotée" pour un contrat qui ne propose que la gestion déléguée — vérifier sur le site officiel

### Génération du slug

Nom du contrat → kebab-case, sans accents, en minuscules.
Exemples : « Linxea Spirit PER » → `linxea-spirit-per`, « meilleurtaux Liberté » → `meilleurtaux-liberte`, « Yomoni Retraite+ » → `yomoni-retraite-plus`
