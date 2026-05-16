---
name: write-contrat-per
description: >-
  Créer ou mettre à jour une fiche de contrat PER (Plan Épargne Retraite)
  individuel. Combine les données du comparatif sinvestir.fr avec des
  recherches sur le site de l'institution pour documenter frais, supports,
  contraintes spécifiques et conditions d'achat. Utiliser quand l'utilisateur
  veut documenter un contrat PER spécifique.
allowed-tools: Read Write Edit WebFetch WebSearch Bash
---

# Créer / mettre à jour une fiche de contrat PER

## Données d'entrée

Le comparatif sinvestir.fr fournit la liste des contrats et des avis. Récupérer les données via le skill `fetch-comparisons` si nécessaire.

### Fiabilité des données sinvestir

- **Données subjectives** (notes, avis, points forts/faibles, appréciations) : utilisables telles quelles, en citant sinvestir comme source
- **Données objectives** (frais, performances, nombre de supports, conditions, contraintes) : DOIVENT être vérifiées et sourcées depuis le site officiel du distributeur ou de l'assureur. Ne pas reprendre les chiffres sinvestir sans vérification

## Processus

1. **Lire les données sinvestir** pour le contrat concerné (`.tmp/per-data.json`)
2. **Rechercher UNIQUEMENT sur le site du distributeur** (et de l'assureur si pertinent) — ne JAMAIS utiliser de sites tiers (blogs, comparateurs, forums comme cleerly.fr, ideal-investisseur.fr, etc.) :
   - Page produit officielle du PER
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
4. **Documenter les contraintes spécifiques** — c'est la valeur ajoutée :
   - Règles d'arbitrage (ex : « arbitrage du fonds euros vers SCPI interdit, versement uniquement »)
   - Limites d'investissement (ex : « 40 % SCPI maximum », « 25 % minimum en UC pour accéder au fonds euros boosté »)
   - Montants minimums par opération (versement initial, versements libres, arbitrage)
   - Conditions de la gestion pilotée (surcoûts, profils disponibles)
   - Conditions de transfert entrant/sortant
   - Pénalités ou délais spécifiques
4. **Rédiger la fiche** en suivant le template ci-dessous
5. **Écrire le fichier** dans `docs/contrats/per/<slug>.md`

## Génération du slug

Nom du contrat → kebab-case, sans accents, en minuscules.
Exemples :
- « Linxea Spirit PER » → `linxea-spirit-per`
- « meilleurtaux Liberté » → `meilleurtaux-liberte`
- « Yomoni Retraite+ » → `yomoni-retraite-plus`

## Template

Voir [assets/contrat-template.md](assets/contrat-template.md) pour le fichier complet.

```markdown
---
nom: NOM_CONTRAT
type: contrat-per
slug: SLUG
distributeur: NOM_DISTRIBUTEUR
assureur: NOM_ASSUREUR
source: simulateurs.sinvestir.fr
derniere-mise-a-jour: YYYY-MM-DD
---

# NOM_CONTRAT

> PER TYPE_PLAN distribué par DISTRIBUTEUR, assuré par ASSUREUR.

## Informations générales
<!-- Mis à jour : YYYY-MM-DD -->

- **Distributeur** : nom
- **Assureur** : nom (solvabilité : XX %)
- **Type** : Assurantiel / Bancaire
- **Modes de gestion** : libre, pilotée, mixte, profilée...
- **Disponibilité** : en ligne / en agence
- **Versement minimum** : XXX EUR
- **Année de création** : XXXX

## Frais
<!-- Mis à jour : YYYY-MM-DD -->

- **Versement** : X %
- **Gestion UC** : X %
- **Gestion fonds euros** : X %
- **Arbitrage** : X %
- **Rente** : X %
- **Surcoût gestion pilotée** : X %
- **Autres frais** : détails
- **Note frais** : X/5

## Fonds euros
<!-- Mis à jour : YYYY-MM-DD -->

- **Fonds disponibles** : nom (garantie XX % — XX % max du contrat)
- **Performance 2024** : X %
- **Performance cumulée 5 ans** : X %
- **Contraintes d'accès** : ex : XX % min en UC requis
- **Note fonds euros** : X/5

## Unités de compte
<!-- Mis à jour : YYYY-MM-DD -->

- **Nombre total d'UC** : X
- **ETF** : X
- **SCPI** : X
- **Titres vifs** : oui / non
- **Rééquilibrage automatique** : oui / non
- **Autres supports** : produits structurés, OPCI, SCI...
- **Note UC** : X/5

## Conditions et contraintes spécifiques
<!-- Mis à jour : YYYY-MM-DD -->

- **Versement initial minimum** : XXX EUR
- **Versements libres minimum** : XXX EUR
- **Versements programmés minimum** : XXX EUR / mois
- **Arbitrage minimum** : XXX EUR
- **Règles d'arbitrage** : ex : « pas d'arbitrage du fonds euros vers SCPI »
- **Limites d'investissement** : ex : « 40 % SCPI max », « 100 % fonds euros possible »
- **Conditions gestion pilotée** : profils, frais, minimum
- **Transfert entrant** : conditions
- **Transfert sortant** : frais (gratuit si > 5 ans, sinon max 1 %)

## Expérience client
<!-- Mis à jour : YYYY-MM-DD -->

- **Avis clients** : X/5 (X avis)
- **App mobile** : oui / non
- **Contact** : téléphone, email, chat, courrier
- **Ergonomie** : appréciation
- **Note SAV** : X/5

## Avis synthétique
<!-- Mis à jour : YYYY-MM-DD -->

- **Note globale** : X/5
- **Points forts** :
  - ...
- **Points faibles** :
  - ...
- **Services complémentaires** : ...

## Sources

- [S'investir — Comparatif PER](https://simulateurs.sinvestir.fr/les-comparateurs/per)
- [DISTRIBUTEUR — Page produit](URL)
- [Autres sources officielles](URL)
```

## Règles

- Bullet points concis, JAMAIS de longs paragraphes
- Chaque section a un commentaire `<!-- Mis à jour : YYYY-MM-DD -->`
- Si une donnée est indisponible, écrire « Non communiqué »
- Si une donnée est incertaine, ajouter `[à vérifier]`
- Les contraintes spécifiques sont ESSENTIELLES : c'est ce qui différencie les fiches d'un simple copier-coller du comparatif
- Les points forts/faibles reprennent les `importantPoints` de sinvestir mais peuvent être enrichis
- Toujours lier vers `docs/enveloppes/per.md` pour les règles générales du PER
- Sources : UNIQUEMENT les sites officiels du distributeur, de l'assureur, et les sources institutionnelles (service-public.fr, economie.gouv.fr, amf-france.org). Ne JAMAIS citer ni utiliser de sites tiers (blogs, comparateurs, forums) comme source de données
