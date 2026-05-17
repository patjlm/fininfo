# Fininfo — Wiki des produits financiers français

## Objectif

Wiki markdown de produits financiers français : enveloppes d'investissement, institutions, gestionnaires, actifs. Toutes les données proviennent de sources officielles.

## Structure

- `docs/enveloppes/` — fiches des enveloppes (Livret A, PEA, AV, PER, etc.)
- `docs/contrats/` — fiches des contrats/produits par catégorie (`per/`, `pea/`, `assurance-vie/`, etc.)
- `docs/institutions/` — fiches des établissements financiers
- `docs/actifs/` — fiches des actifs (fonds, ETF, SCPI, etc.)
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

## Conventions pour les fiches contrats

Ces conventions s'appliquent à tous les skills qui créent ou mettent à jour des fiches de contrats (`write-contrat`, `fetch-comparisons`, `fetch-support-lists`, etc.).

### Fiabilité des données sinvestir

- **Données subjectives** (notes, avis, points forts/faibles, appréciations) : utilisables telles quelles, en citant sinvestir comme source
- **Données objectives** (frais, performances, nombre de supports, conditions, contraintes) : DOIVENT être vérifiées et sourcées depuis le site officiel du distributeur ou de l'assureur. Ne pas reprendre les chiffres sinvestir sans vérification

### Génération du slug

Nom du contrat → kebab-case, sans accents, en minuscules.
Exemples : « Linxea Spirit PER » → `linxea-spirit-per`, « meilleurtaux Liberté » → `meilleurtaux-liberte`, « Yomoni Retraite+ » → `yomoni-retraite-plus`
