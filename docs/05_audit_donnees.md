# Audit des données — résultats observés

Source OpenML 1597, version 1. Empreinte MD5 identique à la référence officielle.

SHA-256 : fdaf12730dc1fc426f318b71349f24f5c5fd00aa1152940be7e7509ae3d89d2a

| Contrôle | Résultat |
|---|---|
| Transactions brutes | 284807 |
| Fraudes brutes | 492 |
| Doublons exacts retirés | 1081 |
| Fraudes parmi les doublons retirés | 19 |
| Transactions retenues | 283726 |
| Colonnes | 31 |
| Valeurs manquantes | 0 |
| Valeurs non finies | 0 |

## Partitions proposées

| Partition | Transactions | Fraudes | Taux | Temps min / max, secondes |
|---|---|---|---|---|
| train | 170235 | 342 | 0.2009% | 0.0 / 120392.0 |
| validation | 56745 | 57 | 0.1004% | 120393.0 / 145233.0 |
| test | 56746 | 74 | 0.1304% | 145234.0 / 172792.0 |

## Décisions et limites

Choix de protocole proposés : conserver la première occurrence de chaque ligne numérique identique, label compris ; ordonner par Time ; répartir environ 60/20/20, en gardant tous les horodatages égaux ensemble. Les indices renvoient aux lignes de données du fichier source à partir de zéro, hors en-tête ARFF.

Les partitions contiennent les deux classes, sont disjointes et respectent un ordre temporel strict. Les indices sont sauvegardés dans data/processed. La suppression de doublons peut aussi retirer des transactions distinctes ayant une représentation identique ; cette décision devra être signalée dans le rapport.

Les deux jours de données, l’absence d’identifiants clients interprétables et le protocole de PCA initial inconnu limitent la portée du benchmark. Le label ne permet pas d’identifier une typologie précise de fraude. Aucun gain de détection ou de temps métier mesuré à ce stade.

La séparation est préparée pour le premier benchmark. Fixer les métriques, seuils et budget de recherche avant de lancer les expériences. Ne pas réajuster le protocole sur les performances du test.

## Reproduction

Depuis le dossier du projet, exécuter `python3 src/audit_data.py` après obtention du fichier ARFF et des métadonnées officiels dans data/raw. Python standard suffit. Le script refuse un fichier dont l’empreinte ne correspond pas à OpenML.
