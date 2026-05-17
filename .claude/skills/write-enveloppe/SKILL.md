---
name: write-enveloppe
description: >-
  Créer ou mettre à jour une fiche d'enveloppe d'investissement française
  (Livret A, PEA, assurance vie, PER, CTO, SCPI, etc.) avec données
  officielles, bullet points concis et sources vérifiables. Utiliser quand
  l'utilisateur veut documenter une enveloppe d'investissement.
allowed-tools: Read Write Edit WebFetch
---

# Créer / mettre à jour une fiche d'enveloppe

## Enveloppes connues

livret-a, ldds, lep, pel, cel, compte-a-terme, assurance-vie, pea, cto, per, scpi-en-direct

## Processus

1. Identifier l'enveloppe demandée
2. Vérifier si `docs/enveloppes/<slug>.md` existe déjà
3. Collecter les données depuis les sources officielles :
   - service-public.fr, economie.gouv.fr
   - amf-france.org, legifrance.gouv.fr
   - banque-france.fr
4. Rédiger ou mettre à jour la fiche en suivant le template
5. Mettre à jour `docs/enveloppes/README.md` si nouvelle fiche

## Règles

- Bullet points concis, JAMAIS de longs paragraphes
- Chaque section a un commentaire `<!-- Mis à jour : YYYY-MM-DD -->`
- Toutes les données factuelles doivent avoir une source URL
- Si une donnée est incertaine, la marquer `[à vérifier]`
- Utiliser la date du jour pour les nouvelles sections

## Template

Voir [assets/enveloppe-template.md](assets/enveloppe-template.md).

### Structure attendue

```markdown
---
nom: Nom Officiel Complet
type: enveloppe
slug: nom-kebab-case
derniere-verification: YYYY-MM-DD
---

# Nom Officiel

> Description en une phrase.

## Caractéristiques principales
<!-- Mis à jour : YYYY-MM-DD -->
- **Plafond** : montant
- **Taux** : taux et conditions
- **Garantie** : type (État, FGDR, FGAP, aucune)
- **Durée** : contraintes de durée

## Fiscalité
<!-- Mis à jour : YYYY-MM-DD -->
- **Pendant la détention** : imposition des gains
- **Au retrait** : imposition (PFU, barème, exonération)
- **Prélèvements sociaux** : taux et conditions
- **Cas particuliers** : abattements, exonérations

## Conditions
<!-- Mis à jour : YYYY-MM-DD -->
- **Âge minimum** : âge requis
- **Résidence fiscale** : conditions
- **Ouverture** : nombre max, pièces requises
- **Versements** : minimum, périodicité
- **Retrait** : conditions, délais, pénalités
- **Clôture** : conditions de fermeture

## Actifs éligibles
<!-- Mis à jour : YYYY-MM-DD -->
- Liste des actifs

## Sources
- [Nom source](URL)
```

## Mise à jour d'une fiche existante

1. Lire la fiche existante
2. Ne modifier QUE les sections concernées
3. Mettre à jour `<!-- Mis à jour -->` des sections modifiées
4. Mettre à jour `derniere-verification` dans le frontmatter
5. Vérifier que les URLs sources sont toujours valides
