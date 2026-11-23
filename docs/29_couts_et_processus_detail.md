# Cadrage détaillé et coûts — scénario hypothétique autorisé
Version du 23 novembre 2026. Aucun chiffre de cette fiche n’est une mesure bancaire ni une facture. Les calculs détaillent les enveloppes déjà retenues, sans modifier les ROI existants.

## Métier AS IS / TO BE
`29_processus_metier.csv` renseigne les sept étapes : acteur/outil, information, durée, coût humain, fréquence et risque. Le volume de 24 000 concerne les **alertes du scénario**, pas toutes les transactions de la banque. Les durées du système sont des hypothèses d’illustration, pas une mesure de latence modèle.
Le travail humain initial représente 6,25 min/alerte. Avant revue supplémentaire, le TO BE suppose 4,25 min, soit 2 min gagnées. L’ajout de 0,5 min de revue donne 4,75 min, donc 1,5 min net gagnée. Les recherches utilisent seulement les sources autorisées ; aucune capacité de recherche RAG n’est ajoutée par cette description cible.
Trois irritants : rareté mesurée des labels (473/283726 après dédoublonnage), volume de fausses alertes à mesurer en banque, durée hypothétique de revue 6,25 min. La couverture PCA interdit d’expliquer des habitudes clients non disponibles.

## Investissement et exploitation
`29_investissement_initial.csv` ventile les 15 000 EUR initiaux entre cadrage, données, diffusion, LLM, UI/API et qualification.
`29_ventilation_couts.csv` ventile exploitation pessimiste/centrale/optimiste : calcul/matériel/électricité, maintenance, supervision technique, stockage/sauvegardes, licences et incidents techniques. Sommes : 10 000 / 8 000 / 7 000 EUR/an.
La revue des dossiers (9 000 EUR/an au centre) et les autres coûts métier (1 000 EUR/an) sont soustraits des gains ; ils ne sont pas inclus une seconde fois dans l’exploitation technique. La réserve incidents couvre les reprises techniques seulement.
Les taux de reprise métier 20/10/5 % sont des **hypothèses**, déjà incluses forfaitairement dans les 0,75/0,5/0,25 min de revue ajoutée ; ne pas les refacturer. Ils ne sont pas les taux d’échec du benchmark LLM.

## Projection et coût par succès
`experiments/results/financial_breakdown.csv` contient la projection mensuelle, le coût par alerte et les trois ROI. Au centre : 666,67 EUR/mois et 0,3333 EUR/alerte d’exploitation supposée.
`finops_allocated_scenario.csv` applique cette allocation hypothétique uniforme aux dix cas TP04 et divise par les contrats réussis. Cela illustre le calcul par succès, **pas** la consommation réelle de chaque architecture. Les trois gardes sont incluses dans les succès de contrat ; leur coût n’est pas confondu avec une inférence réussie. Cette allocation ne permet pas de conclure sur le coût marginal des stratégies.
Le coût API observé est nul ; coût complet réel et énergie électrique restent ND. Aucun tarif fournisseur n’est inventé. Les résultats hypothétiques ne remplacent pas `tp05_mesures.csv`.

## Reproduction
`python src/complete_financial_scenario.py` puis `python src/calculate_roi.py`. Les sommes, le gain de deux minutes et le ROI central sont vérifiés automatiquement dans `financial_checks.json`.
