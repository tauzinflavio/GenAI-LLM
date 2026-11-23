# Manifeste des données — audit réalisé

Source : OpenML 1597, creditcard, version 1.
https://www.openml.org/api/v1/json/data/1597
Fichier : https://openml.org/data/v1/download/1673544/creditcard.arff
Métadonnées et fichier obtenus le 16 novembre 2026.
Licence indiquée par OpenML : « Public ». Conserver ce libellé exact ; modalités détaillées de redistribution non établies.
Usage retenu : benchmark pédagogique local. Données brutes exclues de l’archive partageable.

SHA-256 : fdaf12730dc1fc426f318b71349f24f5c5fd00aa1152940be7e7509ae3d89d2a
MD5 comparé avec succès à la référence OpenML.
Schéma : Time, V1 à V28, Amount, Class. V1 à V28 sont des composantes PCA selon la source. Time est un temps écoulé relatif. Class vaut 1 pour fraude et 0 sinon. Montant en unité non confirmée par la fiche consultée.

Effectifs, contrôles et partitions détaillés dans docs/05_audit_donnees.md et experiments/data_audit.json.
Aucun prétraitement appris ni modèle entraîné. Seuls les indices des partitions sont produits.
Les données ne permettent pas de déduire des pays, marchands, profils clients ou raisons métier spécifiques. Les synthèses LLM resteront limitées aux faits disponibles.
Limites et décision d’accès détaillées dans docs/04_decision_donnees.md.
