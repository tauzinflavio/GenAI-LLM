# Business case pédagogique — trois scénarios

Toutes les valeurs de ce document sont des hypothèses pédagogiques choisies pour une analyse de sensibilité, après autorisation d’un scénario hypothétique. Elles ne proviennent d’aucune banque et ne sont pas déduites du dataset OpenML. Les résultats financiers sont des calculs conditionnels à ces hypothèses.

## Hypothèses
Le scénario représente 24 000 alertes par an et un coût horaire chargé supposé de 45 €. L’investissement initial est supposé égal à 15 000 €. Les gains annexes sont fixés à zéro, et les autres coûts métier à 1 000 € par an. Ces valeurs sont conservées entre scénarios pour isoler l’effet du temps gagné, de la revue supplémentaire et des coûts d’exploitation.

| Variable supposée | Pessimiste | Central | Optimiste |
|---|---|---|---|
| Minutes gagnées avant revue supplémentaire | 0,5 | 2 | 2,5 |
| Minutes de revue ajoutées par alerte | 0,75 | 0,5 | 0,25 |
| Exploitation annuelle | 10 000 € | 8 000 € | 7 000 € |

Les durées ne sont pas des temps observés auprès d’analystes. Les coûts incluent forfaitairement calcul, hébergement éventuel, maintenance, supervision et licences. Une mise en œuvre réelle demanderait une ventilation et des sources.

## Calculs conditionnels

| Scénario | Gain net opérationnel/an | Coût année 1 | ROI année 1 | Retour simple |
|---|---|---|---|---|
| pessimiste | -5500.00 € | 25000.00 € | -122.00 % | non défini |
| central | 26000.00 € | 23000.00 € | 13.04 % | 10.00 mois |
| optimiste | 39500.00 € | 22000.00 € | 79.55 % | 5.54 mois |

Dans le scénario pessimiste, la revue ajoutée dépasse le gain brut de temps. Les coûts entraînent donc une perte supérieure à l’investissement de la première année, ce qui explique un ROI inférieur à −100 %. Dans le scénario central, 36 000 € d’économies brutes moins 9 000 € de revue et 1 000 € d’autres coûts donnent 26 000 € de gain net opérationnel. Après 23 000 € de coûts année 1, le solde est de 3 000 €.

## Seuil de rentabilité central
Avec les autres hypothèses centrales inchangées, le temps brut gagné par alerte doit atteindre environ 1,83 minute pour un ROI année 1 nul. Ce calcul inclut la revue de 0,5 minute et les coûts de la première année. Le seuil concerne le scénario financier ; il ne remplace pas une mesure métier.

Le retour simple utilise l’investissement initial divisé par la marge annuelle après exploitation, puis multiplie par douze. Il ignore l’actualisation, la montée en charge et les variations mensuelles.

## Hypothèses de validation
Pour une future confirmation métier, viser un gain brut de deux minutes par alerte dans le scénario central et mesurer séparément la revue ajoutée. Cet objectif a été choisi après les expériences techniques ; il ne doit pas être présenté comme préenregistré pour les résultats existants. La comparaison devra utiliser des dossiers équivalents et intégrer les reprises.

Aucun gain financier n’est attribué aux fraudes potentiellement évitées, faute de protocole causal et de données autorisées de pertes. La faible conformité des LLM actuels empêche de considérer le gain de temps supposé comme acquis.

## Reproduction
Renseigner docs/hypotheses_roi.csv puis exécuter src/calculate_roi.py. La sortie experiments/roi_scenarios.csv distingue calcul et hypothèse. Le script a été contrôlé sur l’exemple pédagogique du pack et un cas sans retour positif.
