# FraudLab — rapport de projet consolidé

Dossier consolidé du 23 novembre 2026. Groupe : Ahmed, Meriem, Flavio. Interlocuteur, contributions réelles et modalités de remise à confirmer.

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

## Multi-LLM : progression expérimentale
La V1 compare A=SmolLM2-360M et B=Qwen2.5-0.5B avec leurs révisions figées, puis une chaîne A rédacteur/B vérificateur. Elle obtient respectivement 0/10, 1/10 et 4/10 contrats conformes. Le prompt V2 figé avant douze cas séparés améliore B à 8/12 mais dégrade la chaîne à 1/12. Les dénominateurs 10 et 12 restent séparés.

Le TP04 exécute quatre stratégies sur dix nouvelles fixtures gelées : quatre usuelles, deux complexes, quatre cas de stress. A seul atteint 5/10 ; B seul 9/10 ; routing 7/10 ; cascade conditionnelle 9/10. Chaque total inclut trois refus produits par des gardes communes. Sur les sept cas effectivement soumis aux modèles, B et cascade réussissent donc six contrats. La cascade utilise 12 appels contre 7 pour B, sans gain de conformité. Le montant nul reste un échec conservé. L’injection échoue avec A et réussit avec B, routing et cascade sur ce seul cas de confirmation. La cascade n’est pas promue par défaut.

Les traces contiennent routes, modèles, révisions, horodatages, statuts, tokens, erreurs et durées. Limites : deux appels, aucun retry, budgets de tokens et temps, worker interruptible. Quatorze tests d’orchestration simulés ont réussi. Les cas restent construits ; la première campagne TP04 a subi co-charge et panne héritée entre stratégies. Une confirmation vérifie les workers avant chaque stratégie et constitue le tableau courant. L’incident initial est conservé et la répétition n’est pas un test indépendant. Voir docs/05_tp04_benchmark.md.

Le mini-lab M01 distinct comporte 4 extractions, 4 raisonnements et 4 synthèses. Les deux modèles obtiennent 3/12 sur la grille automatique figée, trop peu pour le seuil retenu. La couverture lexicale de synthèse n’est pas une évaluation humaine du sens. Aucun modèle n’est retenu selon cette grille. Voir docs/24_mini_lab_M01.md.

## Fidélité et diversité des générations
Une analyse descriptive complémentaire compare les générations existantes aux 68 fraudes internes tenues à l’écart de chaque générateur, sans accès au test final. Les statistiques KS/Wasserstein marginales, les écarts de corrélation et les distances sont conservés par feature et configuration. À seed 42 / x4 : KS moyen 0,1490, Wasserstein standardisé moyen 0,2319, écart moyen de corrélation 0,2031. Ces valeurs ne sont pas des scores universels de qualité et aucune borne de réussite n’est définie a posteriori.

Toutes les lignes synthétiques acceptées sont distinctes et aucun quasi-doublon train au seuil 1e-6 n’est observé. La distance médiane entre paires synthétiques vaut 5,5268 contre 6,4144 pour les 68 fraudes réelles internes à seed 42 / x4. Tailles différentes, petit nombre de fraudes et sélection par filtre limitent la comparaison. Unicité et absence de copie proche ne démontrent pas la confidentialité. L’utilité aval reste évaluée séparément. Voir experiments/results/generation_quality.csv et docs/25_qualite_generation.md.

## Business case et FinOps
Scénarios entièrement hypothétiques autorisés : 24 000 alertes/an, 45 €/h et investissement initial de 15 000 €. ROI année 1 : pessimiste −122 %, central +13,04 %, optimiste +79,55 %. Le scénario central suppose deux minutes brutes gagnées et 0,5 minute de revue ajoutée par alerte ; le gain n’a pas été observé en banque.

Le workload TP04 dispose de comptes d’appels/tokens et de durées mesurés. Coût API facturé : 0 €. Coût complet réel et coût complet par tâche métier réussie : ND. La réussite du contrat factuel ne mesure pas une efficacité bancaire. B utilise cinq appels de moins que la cascade pour la même conformité observée, soit 41,7 % des appels de cascade évités. Aucun gain énergétique proportionnel n’en est déduit. Voir docs/06_tp05_finops_green_ethique.md.

## Green AI
Les kWh et le CO₂e réels restent non mesurés. Une sensibilité conditionnelle applique 10/25/50 W supposés aux durées du même workload TP04. Facteur RTE 2025 : 20,0 gCO₂e/kWh, consommation française, émissions directes, moyenne historique consultée le 23 novembre 2026. PUE 1 pour le périmètre ordinateur, aucune climatisation de bâtiment estimée. Exclusions : chargement, apprentissage, fabrication, réseau, amont électrique et hors-requêtes. Les valeurs calculées ne constituent pas une empreinte réelle et les petits échantillons limitent leur comparaison.

Source : https://analysesetdonnees.rte-france.com/bilan-electrique-2025/emissions. Fichier : experiments/results/tp05_green_estimates.csv. Les anciens scénarios entièrement fictifs restent identifiés à part.

## Déploiement et résilience TP08
Le service FastAPI existant est adapté au parcours local CPU, autorisé par le TP08. Aucun accès cloud, achat GPU ni déploiement Docker exécuté n’est revendiqué. Le serveur reste sur 127.0.0.1. /healthz mesure l’état de l’API, /readyz celui des deux processus modèles. Une vraie inférence fournit modèle, révision et trace_id, sans prompt dans smoke.json.

Deux paliers utilisent la même requête fictive et Qwen seul : concurrence 1, 12/12 contrats conformes, p95 indicatif 1,993 s ; concurrence 3, 1/18 conforme et 17 rejets 429. Le service borne l’admission à une seule inférence. Le p95 global de 0,279 s au second palier inclut les refus rapides ; il ne signifie pas une meilleure inférence ni une plus grande capacité utile.

Une instance jetable a subi l’arrêt volontaire de son processus writer. health=200, ready=503 et generate=503 ; le redémarrage a produit une nouvelle inférence réelle et conforme en 18,61 s depuis la panne. Une sauvegarde SQLite a été restaurée dans un fichier neuf avec intégrité vérifiée. Les preuves et commandes figurent dans docs/deployment_decision.md et docs/incident_runbook.md.

## Application, données et sécurité
Six écrans relient les expériences réelles, le calcul de score, la génération DDPM, les rapports, l’avis humain et SQLite. Le rapport déterministe reste le défaut. Les nouveaux modes LLM utilisent une orchestration bornée. L’utilisateur peut réactiver les modèles locaux après indisponibilité, sans rejouer automatiquement une demande.

Les requêtes sont contrôlées par schémas, limites de taille et refus des valeurs non finies. L’accès local, le contrôle Host/Origin et les actions bornées protègent le périmètre pédagogique. Aucun compte bancaire n’est modifié. Le journal de service ne contient ni prompt ni sortie libre ; la référence libre de prédiction est hachée avant persistance. La rétention locale est de 30 jours. Le hachage ne constitue pas une anonymisation garantie. Poids, données, SQLite, sauvegardes et secrets sont exclus du dossier GitHub.

## Reproductibilité et limites
Une installation et un réentraînement dans un environnement neuf sur le même Mac ont reproduit les 18 scores de validation sans écart. Les mêmes fichiers de données ont été réutilisés et revérifiés ; ni le test final ni tout le benchmark LLM n’ont été répétés à cette occasion. Le script de test final protège ses résultats existants. Les bibliothèques et modèles sont épinglés, les sources et empreintes documentées.

Les petits jeux de contrats ne mesurent pas une expertise bancaire ni l’équité démographique. Les hypothèses ROI ne prouvent pas un gain métier. La puissance est supposée et les coûts complets inconnus. Le local n’apporte ni SSO, TLS ni disponibilité de production. La validation humaine, le rôle d’interlocuteur, les contributions individuelles et les modalités pédagogiques restent à compléter par le groupe. Le PowerPoint est reporté conformément à la demande de l’utilisateur.

## Décision et dossier
GO sous conditions pour démonstration locale supervisée. NO-GO pour production bancaire autonome et promotion automatique de la cascade. La diffusion est étudiée avec ses échecs, sans supériorité démontrée sur la référence pondérée. Le dossier fournit les PDF C2/C3, le rapport, les cas, sources, configurations, scripts, résultats et preuves. L’import GitHub intervient ensuite, sans publication ni historique de commits inventé.


## Finalisation des TP et du dossier commun
TP01/TP02 sont exécutés et vérifiés, figures et conclusions intégrées à notebooks/ et experiments/tp01,tp02. La synthèse PDF fait3pages. La version PDF courante du rapport fait7pages ; les copies précédentes restent historiques. Le cadrage conserve5pages et la preuveC3 2pages.
Coûts du scénario ventilés, AS IS/TO BE chiffré, reprises et allocation par succès hypothétiques : docs/29_couts_et_processus_detail.md. Aucune modification des métriques du test final. Fiche système : MODEL_CARD.md ; architecture/ADR une page : deliverables/Architecture_ADR_FraudLab.pdf.
Le POC comporte un écran TP & livrables et un atelier de relecture aveugle pour158sorties. Les modèles sont masqués pendant la notation ; aucune note humaine n’est remplie. Interlocuteur, répartition et opérateur restent à décider selon réponse explicite du groupe. Les 50% individuels ne sont pas certifiés par le dossier collectif. Soutenance/PPT exclus.
Tableau de référence : docs/30_matrice_TP_projet_final.md.
