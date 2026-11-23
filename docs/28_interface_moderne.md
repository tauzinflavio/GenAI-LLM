# Interface moderne — 23 novembre 2026

La présentation approuvée a été adaptée aux six écrans de l’application locale : palette indigo, navigation avec repères visuels, cartes arrondies, formulaires et tableaux harmonisés, affichage mobile.

Les routes API, identifiants des contrôles, traitements JavaScript et résultats expérimentaux ont été conservés. Aucun chiffre fictif de la maquette n’a remplacé les données du projet. Aucun service externe ni dépendance graphique distante n’a été ajouté.

## Vérification effectuée

- Navigation entre les six écrans et chargement des métriques sauvegardées.
- Calcul du score de VAL-178208 puis rapport déterministe : contrat respecté.
- Génération DDPM : 4 sorties acceptées sur 4, seed 42.
- Chargement du scénario central : ROI hypothétique 13,0 %.
- Calcul énergie avec 25 W, PUE 1, facteur 20 : résultat explicitement hypothétique.
- Largeur de document égale à 320 px sur chacun des six écrans pour une fenêtre de 320 px. Les tableaux larges défilent dans leur propre zone.
- Aucune erreur console observée durant ces parcours.

Le backend et les prompts sont inchangés ; les benchmarks d’inférence n’ont pas été relancés pour cette modification visuelle. Ces contrôles ne constituent pas une certification d’accessibilité.

## Correction de la structure

La première version conservait trop la disposition initiale. La marque a été déplacée dans la navigation latérale, un bandeau de contexte a été ajouté et le parcours analyste possède désormais un en-tête indigo. Sur fenêtre étroite, la navigation passe en bandeau horizontal.
