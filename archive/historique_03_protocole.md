# Protocole expérimental proposé
Aucune expérience exécutée. Valider et versionner le protocole avant les comparaisons finales.

## Données et séparation
Enregistrer source, licence, version, SHA-256, schéma, effectifs et taux de fraude. Examiner doublons et dépendances entre entités avant de figer les partitions. Préférer une séparation temporelle si les dates sont fiables et le scénario prospectif. Vérifier les effectifs de chaque classe avant de retenir ce plan. Justifier toute alternative.
Ajuster imputation, normalisation et générateur sur train. Utiliser validation pour choisir configurations et seuils. Garder test final indépendant, réel et sans augmentation. Documenter les données vues par chaque composant.

## Comparaisons GenAI
B0 : détecteur sur train original.
B1 : même détecteur avec pondération des classes.
B2 : même détecteur avec suréchantillonnage simple de train.
G1 : même détecteur avec train augmenté par diffusion.
Détecteur initial proposé : régression logistique. Comparer avec mêmes splits, métriques et budgets d'ajustement. Une référence non linéaire pourra suivre.
Ablation prioritaire : deux ratios d'augmentation. Autre facteur possible : nombre de pas. Isoler un facteur à la fois. Noter la taille de train obtenue et les seeds.
Métrique principale proposée : average precision (AP), en précisant l'implémentation. Compléter avec précision, rappel, matrice de confusion, volume d'alertes, temps et ressources. Choisir les seuils sur validation. Définir à l'avance tout budget d'alertes utilisé pour une évaluation de classement.
Contrôler validité, distributions conditionnelles, relations entre variables, diversité, doublons et proximité aux données train. Le test d'utilité aval est central.
Répéter sur plusieurs seeds si possible et rapporter dispersion, effectifs et incertitudes. Les rares positifs peuvent limiter la conclusion.

## Comparaisons LLM
V1 : modèle A rédacteur. V2 : même A plus un modèle B distinct vérificateur. Comparer la sortie finale livrée, avec mêmes dossiers, consignes comparables et même format cible.
Le vérificateur reçoit les faits sources. Sa réponse ne sert pas de vérité de référence. Utiliser une grille humaine commune, si possible avec configuration masquée.
Exclure de l'entrée le label réel et les informations futures. Un score ne démontre pas les raisons d'une fraude. Tracer l'origine des explications affichées.
Mesurer affirmations non étayées, omissions, respect du format, erreurs détectées/manquées et fausses alertes de vérification. Mesurer aussi p50/p95, tokens, appels, retries et coût total.
Les dix scénarios JSONL testent le pipeline une fois instanciés. Ils complètent un benchmark indépendant plus large.

## Green AI
Définir unité fonctionnelle et périmètre. Séparer entraînement diffusion, inférence détecteur et appels LLM. Distinguer mesure, calcul et estimation. Documenter matériel, durée, PUE et facteur carbone si utilisés, avec sources et incertitudes. Les API opaques limitent la précision ; le prix ne permet pas directement de calculer le CO₂e.

## Traçabilité
Conserver code/version, split, config, seed, métrique, unité, statut, preuve et limites. Statuts autorisés : mesuré, calculé, hypothétique, non mesuré. Rapporter aussi toute absence de gain.
