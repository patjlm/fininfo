---
name: write-contrat-av
description: >-
  Créer ou mettre à jour une fiche de contrat d'assurance vie. Recherche les
  informations sur les sites officiels du distributeur et de l'assureur pour
  documenter frais, supports, contraintes spécifiques et conditions. Utiliser
  quand l'utilisateur veut documenter un contrat d'assurance vie spécifique.
allowed-tools: Read Write Edit WebFetch WebSearch Bash
---

# Créer / mettre à jour une fiche de contrat d'assurance vie

## Données d'entrée

Le comparatif sinvestir.fr fournit la liste des contrats et des avis. Récupérer les données via le skill `fetch-comparisons` (type `life-insurance`) si nécessaire.

### Fiabilité des données sinvestir

- **Données subjectives** (notes, avis, points forts/faibles, appréciations) : utilisables telles quelles, en citant sinvestir comme source
- **Données objectives** (frais, performances, nombre de supports, conditions, contraintes) : DOIVENT être vérifiées et sourcées depuis le site officiel du distributeur ou de l'assureur. Ne pas reprendre les chiffres sinvestir sans vérification

## Processus

1. **Lire les données sinvestir** pour le contrat concerné (`.tmp/life-insurance-data.json`)
2. **Rechercher UNIQUEMENT sur le site du distributeur** (et de l'assureur si pertinent) — ne JAMAIS utiliser de sites tiers (blogs, comparateurs, forums comme cleerly.fr, ideal-investisseur.fr, etc.) :
   - Page produit officielle de l'assurance vie
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
   - Conditions de rachat partiel/total
   - Avance sur contrat
   - Pénalités ou délais spécifiques
5. **Rédiger la fiche** en suivant le template ci-dessous
6. **Écrire le fichier** dans `docs/contrats/assurance-vie/<slug>.md`

## Génération du slug

Nom du contrat → kebab-case, sans accents, en minuscules.
Exemples :
- « Linxea Spirit 2 » → `linxea-spirit-2`
- « Lucya Cardif » → `lucya-cardif`
- « Boursorama Vie » → `boursorama-vie`

## Template

Voir [assets/contrat-template.md](assets/contrat-template.md) pour le fichier complet.

```markdown
---
nom: NOM_CONTRAT
type: contrat-assurance-vie
slug: SLUG
distributeur: NOM_DISTRIBUTEUR
assureur: NOM_ASSUREUR
derniere-mise-a-jour: YYYY-MM-DD
---

# NOM_CONTRAT

> Assurance vie distribuée par DISTRIBUTEUR, assurée par ASSUREUR.

## Informations générales
<!-- Mis à jour : YYYY-MM-DD -->

- **Distributeur** : nom
- **Assureur** : nom (solvabilité : XX %)
- **Type** : multisupports / monosupport
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
- **Surcoût gestion pilotée** : X %
- **Frais de rachat** : X %
- **Autres frais** : détails
- **Note frais** : X/5

## Fonds euros
<!-- Mis à jour : YYYY-MM-DD -->

- **Fonds disponibles** : nom (garantie XX % — XX % max du contrat)
- **Performance 2024** : X %
- **Performance 2025** : X %
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
- **Rachat partiel minimum** : XXX EUR
- **Avance sur contrat** : conditions
- **Clause bénéficiaire** : standard / libre / démembrée

## Fiscalité
<!-- Mis à jour : YYYY-MM-DD -->

- **Avant 8 ans** : PFU 30 % (12,8 % IR + 17,2 % PS) ou barème IR + PS
- **Après 8 ans** : abattement annuel 4 600 EUR (célibataire) / 9 200 EUR (couple) puis 24,7 % (7,5 % + 17,2 % PS) ou barème IR + PS
- **Transmission** : abattement 152 500 EUR/bénéficiaire (versements avant 70 ans) ; 30 500 EUR tous bénéficiaires confondus (versements après 70 ans)

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

- [S'investir — Comparatif Assurance Vie](https://simulateurs.sinvestir.fr/les-comparateurs/assurance-vie)
- [DISTRIBUTEUR — Page produit](URL)
- [Autres sources officielles](URL)
```

## Règles

- Bullet points concis, JAMAIS de longs paragraphes
- Chaque section a un commentaire `<!-- Mis à jour : YYYY-MM-DD -->`
- Si une donnée est indisponible, écrire « Non communiqué »
- Si une donnée est incertaine, ajouter `[à vérifier]`
- Les contraintes spécifiques sont ESSENTIELLES : c'est ce qui différencie les fiches d'un simple copier-coller du comparatif
- Toujours lier vers `docs/enveloppes/assurance-vie.md` pour les règles générales de l'assurance vie
- Sources : UNIQUEMENT les sites officiels du distributeur, de l'assureur, et les sources institutionnelles (service-public.fr, economie.gouv.fr, amf-france.org). Ne JAMAIS citer ni utiliser de sites tiers (blogs, comparateurs, forums) comme source de données
