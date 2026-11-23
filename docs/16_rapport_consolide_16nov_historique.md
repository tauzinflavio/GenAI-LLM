# FraudLab — rapport de projet consolidé

Version de travail du 16 novembre 2026. Les membres et échéances finales restent à renseigner.

## Problème et objectifs
Le scénario pédagogique concerne un analyste chargé de revoir des alertes de transactions par carte. Le système étudie deux contributions génératives. La diffusion produit des transactions synthétiques pour enrichir l’entraînement d’un détecteur. Les LLM produisent et vérifient des rapports factuels d’alertes. Le parcours métier AS IS et les chiffres financiers représentent un scénario hypothétique autorisé, sans observation d’une banque réelle.

Les questions scientifiques sont l’utilité de l’augmentation par diffusion, l’apport d’une chaîne Multi-LLM face aux modèles seuls et l’arbitrage entre qualité, latence et ressources. Les expériences existantes sont exploratoires. Les objectifs métier chiffrés introduits ensuite servent à préparer une confirmation future.

## Architecture et expérience utilisateur
Le traitement hors ligne prépare les partitions, entraîne les modèles et conserve les artefacts. Le POC en ligne relie une interface web à une API FastAPI et un stockage SQLite. L’analyste sélectionne une transaction de validation, calcule le score, consulte un rapport déterministe ou LLM et enregistre son avis. Une page permet de générer des vecteurs réels avec le DDPM ; les configurations et sorties sont conservées.

Les modes LLM restent expérimentaux. La conformité du rapport est contrôlée indépendamment. Une sortie non conforme est signalée. Les permissions du POC couvrent des avis pédagogiques ; aucune opération bancaire n’est réalisée. L’accès analyste est simulé et le serveur reste local.

## Données et gouvernance
OpenML 1597 version 1 contient 284 807 transactions brutes, dont 492 fraudes. Après retrait de 1 081 doublons exacts, l’étude conserve 283 726 lignes et 473 fraudes. L’empreinte du fichier a été comparée à celle publiée par OpenML. Le manifeste conserve la provenance et les limites de licence déclarée.

Les partitions chronologiques contiennent 170 235 lignes de train, 56 745 de validation et 56 746 de test, dont respectivement 342, 57 et 74 fraudes. Les horodatages égaux restent groupés. Les transformations apprises utilisent le train. Le label n’est pas communiqué aux LLM. Les composantes PCA anonymisées, la courte période et l’absence d’identifiants clients interprétables limitent l’analyse et la généralisation.

## Méthodes GenAI
Le détecteur est une régression logistique. Les références utilisent les données originales, la pondération des classes et le rééchantillonnage aléatoire. Les candidats ajoutent des transactions générées par un DDPM gaussien inconditionnel, entraîné sur la classe fraude. Le réseau MLP possède deux couches cachées de 128 unités, avec 100 pas et 2 000 mises à jour.

Les ratios visés d’ajout sont x1 et x4 ; chaque baseline de rééchantillonnage reçoit autant d’ajouts que le candidat DDPM a de sorties acceptées. Trois seeds permettent d’examiner la variabilité. La normalisation du générateur est ajustée sur son sous-ensemble interne de train. Un contrôle interne exclu de son apprentissage mesure la prédiction du bruit.

Le générateur travaille sur V1 à V28 et log1p(Amount). Les valeurs invalides sont rejetées et comptées. La proximité aux données d’apprentissage est examinée ; elle ne constitue pas une garantie générale de confidentialité.

## Résultats GenAI et décision
La référence pondérée a été retenue avant lecture du test final sur la base de la validation. Sur le test, son AP est 0.7442, sa précision 0.9600 et son rappel 0.6486, au seuil figé de validation. Le choix du seuil était exploratoire et ne reflète pas un coût métier validé.

La diffusion x4, seed 42, obtient une AP de 0,7551 contre 0,7442 pour cette référence. L’intervalle bootstrap de l’écart couvre zéro. La supériorité de la diffusion n’est donc pas établie. Les résultats de toutes les configurations sont conservés ; le système ne remplace pas sa configuration retenue à partir du test.

## Mono-LLM et Multi-LLM
SmolLM2-360M-Instruct et Qwen2.5-0.5B-Instruct sont exécutés localement avec leurs révisions figées. Les comparaisons portent sur A seul, B seul et A rédacteur suivi de B vérificateur. Elles utilisent les mêmes dossiers et critères pour une expérience donnée. Les durées de la chaîne incluent les deux appels.

La V1 comporte dix cas fictifs et la comparaison de prompts V2 douze nouveaux cas séparés. Les contrôles automatiques portent sur le format et la copie de faits. Sur le jeu séparé, le prompt initial atteint 5/12 en chaîne ; le nouveau prompt atteint 8/12 avec B seul mais seulement 1/12 en chaîne. La dépendance au modèle est forte. Le rapport déterministe reste le défaut applicatif. L’annotation humaine reste à compléter et ces contrats ne mesurent pas une expertise bancaire.

## Business case hypothétique
Les scénarios autorisés supposent 24 000 alertes annuelles et 45 €/h. L’investissement initial est de 15 000 €. Les variations portent sur le gain brut de temps, la revue ajoutée et les coûts d’exploitation. Aucune de ces valeurs n’est une mesure bancaire. Les formules et sources d’hypothèses figurent dans docs/14_business_case_hypothetique.md.

| Scénario | Gain net opérationnel/an | Coût année 1 | ROI année 1 |
|---|---|---|---|
| pessimiste | -5500 € | 25000 € | -122.00 % |
| central | 26000 € | 23000 € | 13.04 % |
| optimiste | 39500 € | 22000 € | 79.55 % |

Le scénario central est rentable sous ses hypothèses, mais les expériences ne démontrent pas le gain de temps supposé. Le scénario pessimiste reste déficitaire. La rentabilité centrale nécessite environ 1,83 minute brute gagnée par alerte avec les autres paramètres inchangés.

## Ressources, énergie et coût
Les durées, appels et tokens sont mesurés. L’inférence locale ne génère pas de coût API facturé. Les coûts complets et la puissance réelle ne sont pas mesurés. Trois scénarios environnementaux utilisent des puissances et facteurs carbone fictifs explicitement indiqués. Ils couvrent l’inférence seule et servent à la sensibilité. Ils excluent notamment chargement, apprentissage, fabrication et réseau. Les résultats ne constituent pas une empreinte carbone réelle de la solution.

## Reproductibilité et vérifications
Les configurations, paramètres, seeds, versions de modèles, partitions et sorties sont conservés. Les scripts séparent audit, expérience GenAI, test final, inférences LLM et calcul ROI. Le script de test final refuse une seconde évaluation automatique si ses résultats existent. Les archives de partage excluent données brutes, poids et base locale.

Les quatorze contrôles API enregistrés sont passés. Ils couvrent les rapports, la génération, les avis, la persistance et plusieurs refus. Des parcours ont été vérifiés dans le navigateur. La mise en page complète, les tests de charge et la validation humaine restent à poursuivre.

## Limites et suite
Les résultats techniques limitent l’adoption du générateur et de la chaîne LLM. Une nouvelle amélioration demanderait un protocole et des données indépendantes adaptés. Les scénarios métier et carbone doivent être confirmés avant toute décision d’usage réel.

Avant remise, compléter les membres, responsabilités et dates, réaliser l’annotation humaine, vérifier les documents C2/C3 mis en page et préparer la présentation. L’analyse scientifique et la correspondance au code sont dans docs/13_analyse_scientifique.md. Les preuves expérimentales sont dans experiments et tests.
