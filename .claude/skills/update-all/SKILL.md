---
name: update-all
description: >-
  Mettre à jour en masse toutes les fiches de contrats financiers : vérification
  du cookie sinvestir, récupération des données, lancement d'agents en parallèle
  par contrat, validation finale et rapport des erreurs avec suggestions
  d'amélioration des skills. Utiliser quand on veut rafraîchir l'ensemble des
  fiches AV, PER, PEA, CTO, etc.
allowed-tools: Read Write Edit Bash Agent WebFetch WebSearch
---

# Mise à jour en masse des fiches de contrats

## Vue d'ensemble

Orchestration complète en 5 phases :

1. Cookie + récupération sinvestir (délégué à `fetch-comparisons`)
2. Construction du catalogue de contrats à traiter
3. Lancement d'agents en parallèle (un par contrat, délégués à `write-contrat`)
4. Validation finale (`make readmes` + `make check`)
5. Rapport et améliorations continues

## Paramètres

| Paramètre | Défaut | Options |
|---|---|---|
| Types | tous | `per`, `life-insurance`, `pea`, `cto`, `scpi` |
| Modèle agents | `sonnet` | `sonnet`, `haiku`, `opus` |
| Scope | existants + nouveaux | existants seulement, liste de contrats spécifiques |

## Phase 1 — Cookie et récupération sinvestir

Lire et appliquer le skill [`fetch-comparisons`](../fetch-comparisons/SKILL.md) pour :
- Vérifier le cookie `cookie.json` et sa validité
- Récupérer les données pour chaque type demandé → `.tmp/<type>-data.json`

Arrêter si le cookie est invalide — ne pas continuer avec des données potentiellement incomplètes.

## Phase 2 — Catalogue des contrats

Pour chaque type récupéré, construire la liste des contrats à traiter :

1. Lire `.tmp/<type>-data.json` — chaque entrée a `id`, `name`, `data.general.distributor`, `data.general.insurer`
2. Lister les `.md` dans `docs/contrats/<dossier>/` (hors `README.md`)
3. Lire le frontmatter de chaque fichier existant pour faire la correspondance avec les entrées sinvestir
4. Classifier :
   - **À mettre à jour** : fichier existant + entrée sinvestir correspondante
   - **Nouveaux** : entrée sinvestir sans fichier (créer, ou confirmer avec l'utilisateur si scope = existants seulement)
   - **À ignorer** : entrées hors scope (ex: "S'investir Conseil" = service interne sinvestir)

**Correspondances types → dossiers :**

| Type API | Dossier | Skill |
|---|---|---|
| `per` | `docs/contrats/per/` | `write-contrat` |
| `life-insurance` | `docs/contrats/assurance-vie/` | `write-contrat` |
| `pea` | `docs/contrats/pea/` | `write-contrat` |
| `cto` | `docs/contrats/cto/` | `write-contrat` |
| `scpi` | `docs/contrats/scpi/` | `write-scpi` |

**Règles de correspondance :**

Correspondre par `distributeur + assureur` plutôt que par nom seul — sinvestir peut différer du nom officiel.

Pièges connus (voir aussi [AGENTS.md](../../AGENTS.md#fiabilité-des-données-sinvestir)) :
- sinvestir peut inverser assureur et distributeur — toujours indiquer les deux dans le prompt agent
- Un distributeur peut avoir plusieurs contrats distincts (ex: Placement Direct a 3 AV)

## Phase 3 — Agents en parallèle

Lancer **tous les agents en `run_in_background: true`** avec le modèle spécifié.

Chaque agent suit le skill [`write-contrat`](../write-contrat/SKILL.md) (ou `write-scpi` pour les SCPI). Le prompt doit inclure :

```
Projet: /home/patmarti/dev/patjlm/fininfo
Tâche: [Mettre à jour / Créer] la fiche du contrat [TYPE] "[NOM]".
Fichier [existant / à créer]: docs/contrats/[dossier]/[slug].md
Données sinvestir: .tmp/[type]-data.json (cherche name="[NOM]" ou distributeur="[DIST]" + assureur="[ASS]")
Distributeur: [DIST] / Assureur: [ASS]

Instructions:
1. Lire AGENTS.md
2. Lire .claude/skills/write-contrat/SKILL.md et appliquer le processus

[Si Linxea: utiliser fetch-linxea-funds pour la liste des supports.]

Ne pas modifier README.md. Ne pas exécuter make check ni make readmes.
```

**Précautions :**
- Chaque agent écrit dans un fichier distinct → pas de conflit
- Si un site bloque le scraping (403, timeout) : trouver une source alternative (PDF officiel, distributeur secondaire) et le signaler dans le résultat

## Phase 4 — Validation finale

```bash
make readmes
make check
```

Si `make check` échoue : lire les erreurs, corriger les fichiers fautifs, relancer jusqu'à succès.

## Phase 5 — Rapport et améliorations continues

### Rapport

Tableau récapitulatif par contrat : statut (✅ mis à jour / 🆕 créé / ❌ erreur) + corrections notables.

Regrouper par catégorie : corrections factuelles, nouvelles données, sites inaccessibles, nouveaux contrats, erreurs.

### Améliorations

Identifier les problèmes systématiques et proposer des diffs sur :
- `AGENTS.md` : si un type d'erreur sinvestir revient sur plusieurs contrats
- `write-contrat/SKILL.md` : si des instructions étaient ambiguës ou manquantes
- Templates `write-contrat/assets/` : si des agents ont créé des sections non prévues

Proposer sous forme de diff, ne jamais appliquer sans confirmation.
