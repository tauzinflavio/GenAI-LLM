# Vérification de l’interface et reproduction

## Installation séparée
Un nouvel environnement Python 3.14 a été créé sur le même Mac. Toutes les versions de requirements.txt ont été installées. Le code et les résultats de référence ont été copiés dans un dossier de reproduction distinct.

Le même fichier ARFF public et les mêmes poids LLM ont été réutilisés localement pour éviter un téléchargement supplémentaire. Les entrées partagées n’ont pas été modifiées. L’audit a de nouveau contrôlé l’empreinte et reconstruit les partitions.

## Expériences reproduites
Les détecteurs et les trois DDPM ont été réentraînés dans ce nouvel environnement. Les 18 lignes de comparaison retrouvent AP, seuils, précision, rappel, nombre d’alertes et taille de train. L’écart maximal observé entre les tableaux de scores de validation est nul. Les indices des trois partitions sont identiques.

Le test final n’a pas été réévalué. Le benchmark complet des LLM n’a pas été répété. Une exécution mono puis Multi-LLM a cependant été contrôlée dans l’application lancée avec le nouvel environnement. Les limites interplateformes restent ouvertes.

## Parcours API
Quatorze contrôles fonctionnels ont été répétés avec succès dans l’application du nouvel environnement. Six contrôles supplémentaires passent également, dont JSON tronqué, NaN, Infinity, corps trop volumineux et origines/hôtes refusés. Les preuves sont dans experiments/application_checks_reproduction.json et experiments/api_boundary_checks.json.

La revue a conduit à refuser explicitement les constantes JSON non finies et à limiter la lecture du corps. Le statut de disponibilité LLM vérifie les fichiers de poids. Le frontend efface les anciennes erreurs au lancement d’une action et remplace un indicateur d’exécution par un message approprié lorsqu’un rapport échoue.

## Interface à 320 pixels
Les six écrans ont été parcourus à 320 pixels CSS. La largeur du document reste égale à 320 pixels pour chacun. Les tableaux disposent d’un défilement interne. Une capture de la vue d’ensemble a été inspectée.

Le contraste du pied de page a été renforcé, l’écran actif est indiqué avec aria-current et les contrôles sur pointeur grossier ont une hauteur minimale de 44 pixels. Cette revue ne remplace pas un audit d’accessibilité complet, un lecteur d’écran ou un test sur appareil physique.

## Installation du paquet de partage
Les archives excluent les données brutes et les poids. Après création de l’environnement et installation des dépendances, exécuter src/prepare_demo.py. Ce script obtient les entrées manquantes, refait l’audit et reconstruit les artefacts de détection/diffusion nécessaires. Il télécharge les poids LLM manquants aux révisions figées.

Le téléchargement représente environ 151 Mo de données et 1,6 Go de poids LLM. La préparation conserve les rapports archivés et ne réévalue pas le test final. Les résultats peuvent dépendre du matériel et des versions ; la présente reproduction concerne seulement le même Mac et les versions figées.

Pour répéter les parcours API avec le serveur lancé, exécuter tests/check_api.py avec --base-url pointant sur le port choisi. Les contrôles génèrent de véritables événements de démonstration dans la base locale.


## Contrôles de préparation du 23 novembre 2026
Les nouvelles suites comptent 16 contrôles API, 11 contrôles de service/minimisation et 14 tests d’orchestration simulés, tous réussis. Les preuves sont dans application_checks_latest.json, service_safety.json et tp04_robustness.json. Ces tests portent sur le fonctionnement et les contrôles ; ils ne constituent pas une validation humaine des rapports.

Les six écrans ont été revérifiés à 320 pixels sans débordement du document ; les tableaux longs restent dans leurs zones de défilement. Les parcours score/rapport, cascade, DDPM, saisie invalide puis correction, ROI, scénario énergie et journal ont été examinés. Les tableaux affichent la confirmation TP04, pas la campagne initiale avec panne héritée. Le contrôle n’est pas un audit complet d’accessibilité.

La récupération ciblée après arrêt d’un worker a été exécutée avec une nouvelle inférence réelle : recovery_endpoint.json. Le premier échec de readiness est conservé et la correction retestée. Une vraie panne de service et reprise complète ainsi qu’une restauration SQLite indépendante sont également documentées. Les PDF C2/C3, rapport consolidé et fiche M01 ont été rendus et leurs 14 pages inspectées ; les glyphes de sous-indices non supportés ont été remplacés par une écriture lisible.

Un contrôle de restauration du paquet sans ses artefacts reconstruits est consigné dans experiments/results/package_restore.json. Il réutilise les données et les poids locaux autorisés ainsi que l’environnement existant ; il ne prouve pas un nouveau téléchargement ni une nouvelle installation sur une autre machine. Le préparateur reconstruit les artefacts dans une racine temporaire puis ne copie que les fichiers nécessaires à la démonstration, pour préserver les métriques scientifiques archivées. Aucun test final n’est réévalué lors de cette préparation.
