# Résultats et décisions — version expérimentale du 16 novembre 2026

## Détection sur test final
La configuration a été choisie sur validation avant lecture des performances de test. Le modèle retenu pour le POC est la régression logistique pondérée, seed 42, au seuil choisi sur validation. Les autres configurations sont des comparateurs. Aucun nouveau réglage n’a été choisi après examen du test.

Test de 56 746 transactions, dont 74 fraudes. Les seuils sont figés à partir de la validation. Les métriques au seuil ne représentent donc pas un optimum sur test.

| Configuration, seed 42 | AP | Précision | Rappel | VP / FP / FN |
|---|---|---|---|---|
| B0_original | 0.6946 | 0.7143 | 0.6757 | 50 / 20 / 24 |
| B1_class_weight | 0.7442 | 0.9600 | 0.6486 | 48 / 2 / 26 |
| B2_random_over_x1 | 0.7278 | 0.7286 | 0.6892 | 51 / 19 / 23 |
| G1_ddpm_x1 | 0.7285 | 0.7619 | 0.6486 | 48 / 15 / 26 |
| B2_random_over_x4 | 0.7535 | 0.7705 | 0.6351 | 47 / 14 / 27 |
| G1_ddpm_x4 | 0.7551 | 0.7833 | 0.6351 | 47 / 13 / 27 |

L’écart AP diffusion x4 moins pondération, seed 42, est 0.0110. L’intervalle bootstrap apparié stratifié à 95 % est [-0.0601, 0.0843], sur 300 réplications. Il couvre zéro. Cette expérience ne démontre pas une supériorité de la diffusion. Le bootstrap par lignes suppose une indépendance que l’absence d’identifiants clients empêche de vérifier complètement.

Le test final a été évalué une fois avec le script dédié. Les scores sont conservés pour audit. Les futures améliorations demanderont un nouveau protocole ou de nouvelles données indépendantes pour une confirmation fiable.

## LLM locaux et comparaison architecturale
Deux modèles ouverts ont été téléchargés et exécutés localement sur CPU, avec révisions figées dans configs/llm_models.json. Le premier rédige un rapport JSON ; le second intervient seul ou comme vérificateur correcteur. Les générations sont greedy, avec un plafond de 100 nouveaux tokens. Les prompts restent en anglais pour cette première preuve.

Le jeu contient dix dossiers fictifs comprenant données manquantes, absence de contexte, instruction malveillante et demande hors périmètre. Il évalue un contrat de format et de copie de faits. Il ne constitue pas une évaluation d’expertise bancaire ni un échantillon représentatif d’alertes réelles.

| Configuration | Contrats stricts réussis | Latence p95 |
|---|---|---|
| A_mono | 0 / 10 | 1.995 s |
| A_plus_B | 4 / 10 | 4.542 s |
| B_mono | 1 / 10 | 2.188 s |

Le modèle A copie souvent les champs d’entrée sans respecter le schéma demandé. B améliore certaines sorties de A, mais reste insuffisant. Un échec de contrat peut provenir de clés manquantes, d’une décision incorrecte ou de balises Markdown autour d’un JSON correct. Il faut consulter les critères séparés et les sorties brutes avant toute interprétation.

Le vérificateur n’est pas la vérité de référence. Les règles de contrôle déterministes constituent le premier filet de validation. L’application indique les sorties non conformes. Les avis de l’analyste sont enregistrés séparément. L’annotation humaine des trente sorties est à compléter dans experiments/llm_v1/human_review.csv.

Ces modèles ont été choisis pour un POC local sans abonnement API. La faible conformité observée motive une prochaine expérience de prompt et de schéma, puis une évaluation sur de nouveaux cas. Le gain métier d’un LLM reste à démontrer face à une synthèse déterministe.

## POC applicatif
Le prototype relie une interface web, une API FastAPI et une base SQLite locale. Il permet de calculer un score, exécuter un rapport déterministe ou LLM, générer réellement avec le DDPM, consigner un avis et consulter le journal. Le profil analyste est simulé, le serveur doit rester lié à 127.0.0.1.

Les modèles de détection utilisent 29 entrées. Le montant est transformé en log1p ; les composantes PCA sont normalisées à partir du train. Time sert à la séparation et reste exclu du détecteur. Le score pondéré n’est pas une probabilité calibrée et peut être très proche de 1. Le label de test ou validation n’est transmis ni au rapport LLM ni au calcul en application.

Les 14 contrôles API enregistrés sont passés. Les vérifications couvrent score, rapports déterministe/mono/multi, génération, persistance, schéma invalide, montant négatif, référence inconnue, action non permise et limite de génération. Un parcours navigateur a également été vérifié. La validation visuelle exhaustive et les tests de charge restent à faire.

## Ce qui reste ouvert
Les informations d’équipe, l’observation métier, les sources financières, les trois scénarios de ROI, l’annotation humaine et la quantification environnementale doivent encore être complétés. Les supports du cours fixent les exigences ; ils ne fournissent pas ces valeurs propres à notre groupe. Les dates finales restent à confirmer.
