# Décision initiale sur les données

## Source vérifiée
La fiche officielle OpenML du dataset 1597, version 1, décrit le jeu creditcard et renseigne la licence par la valeur « Public ». Cette valeur est conservée telle quelle ; elle ne constitue pas une licence détaillée de redistribution.
Source : https://www.openml.org/api/v1/json/data/1597
Fichier référencé : https://openml.org/data/v1/download/1673544/creditcard.arff

La documentation annonce 284 807 transactions, dont 492 fraudes, sur deux jours en septembre 2013. V1 à V28 sont des composantes PCA. Time représente les secondes écoulées depuis la première transaction ; Amount représente le montant ; Class vaut 1 pour fraude et 0 sinon. Ces nombres sont des caractéristiques déclarées par la source, à confronter à l'audit du fichier.

## Choix proposé
Retenir cette version publique pour un premier benchmark pédagogique local, avec conservation des métadonnées et vérification de l'empreinte publiée. Ne pas inclure les données brutes dans l'archive partageable. Les modalités de redistribution restent à vérifier si une publication des données est envisagée.

## Portée scientifique
Le test prospectif sera étudié via une séparation chronologique. Deux jours constituent une fenêtre courte, insuffisante pour conclure à une généralisation opérationnelle à long terme. Aucun identifiant de client ou marchand n'est décrit dans le schéma, donc leur indépendance entre partitions ne pourra pas être contrôlée. La PCA a été appliquée avant publication ; son protocole d'ajustement n'est pas documenté dans la fiche, ce qui limite les garanties d'absence de fuite au niveau de cette transformation initiale.

## Conséquence pour les LLM
Les variables PCA ne permettent pas une explication sémantique des comportements bancaires. Le rédacteur doit résumer les faits accessibles, les scores et les contrôles à effectuer. Toute référence à un pays, un marchand ou un historique client exige des données supplémentaires autorisées. Les fixtures de tests complémentaires devront rester explicitement pédagogiques.

## Référence demandée par la source
Andrea Dal Pozzolo, Olivier Caelen, Reid A. Johnson et Gianluca Bontempi. Calibrating Probability with Undersampling for Unbalanced Classification. IEEE CIDM, 2015. Référence mentionnée par OpenML ; analyse de l'article à réaliser.
