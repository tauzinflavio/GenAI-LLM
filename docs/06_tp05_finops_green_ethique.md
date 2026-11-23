# TP05 — FinOps, Green AI et éthique
Ahmed, Meriem, Flavio — 23 novembre 2026. Interlocuteur principal et répartition réelle à confirmer.

## Unité fonctionnelle et preuve
Unité disponible : un rapport conforme au contrat factuel sur une fixture autorisée, ou un refus attendu correctement produit par la garde commune. Cela ne mesure pas la réussite métier d’un analyste. Même workload TP04 de dix cas pour les quatre stratégies, avec hash, sorties et révisions de modèles. Séparer les trois gardes et les sept cas d’inférence. Annotation humaine attendue.

| strategy | passes | model_passes | calls | input_tokens | output_tokens | latency_p95 |
|---|---|---|---|---|---|---|
| cascade | 9 | 6 | 12 | 4480 | 416 | 4.120 |
| mono_a | 5 | 2 | 7 | 2694 | 298 | 3.595 |
| mono_b | 9 | 6 | 7 | 2493 | 169 | 1.866 |
| routing | 7 | 4 | 7 | 2605 | 221 | 1.982 |

## FinOps et levier exécuté
Les appels et tokens proviennent des traces, et non d’une estimation tarifaire. Aucun appel API facturé. Le coût API du lot est 0 €. Coût complet réel, allocation du matériel, électricité et temps humain réel : ND. Coût complet par succès : ND. Formule à appliquer lorsque les postes sont connus : (variables du lot + coûts fixes alloués + revue et reprises) / tâches réussies. Si zéro succès, le ratio est non défini, pas nul.

Le levier est la cascade conditionnelle plafonnée à deux appels, sans retry. Elle obtient 9/10 contre 5/10 pour A seul mais demande 12 appels contre 7. B seul atteint aussi 9/10 avec 7 appels. Le choix de B plutôt que la cascade économise donc 5/12 = 41,7 % des appels sur ce workload, à conformité observée égale. Les tokens, latences, prix et énergie ne sont pas proportionnels aux appels ; aucune baisse de CO₂ n’en est déduite. Les p95 restent descriptifs ; la première campagne avec co-charge et panne héritée est conservée comme incident et remplacée par une confirmation.

Le scénario métier central suppose 24 000 alertes/an et 8 000 € d’exploitation annuelle, soit environ 0,333 €/alerte pour cette enveloppe. Cette division est une projection hypothétique, pas le coût mesuré du LLM ni le coût par tâche réussie. ROI année 1 hypothétique 13,04 %. Le contrôle humain supplémentaire est comptabilisé séparément. Références et scénarios dans docs/14_business_case_hypothetique.md.

## Green AI et périmètre
Matériel identifié : Apple M2, 8 Go. Inférence locale CPU, aucune API distante. Durées des requêtes mesurées ; watts, kWh et CO₂e réels non mesurés. Aucun compteur matériel autorisé n’a été utilisé. La durée n’est pas une mesure d’énergie.

experiments/results/tp05_green_estimates.csv calcule une sensibilité à 10, 25 et 50 W, puissances entièrement hypothétiques. Le facteur de 20,0 gCO₂e/kWh provient de RTE, Bilan électrique 2025, intensité moyenne de consommation française en émissions directes, consulté le 23 novembre 2026 : https://analysesetdonnees.rte-france.com/bilan-electrique-2025/emissions. C’est un proxy historique annuel, pas le facteur horaire ni une ACV complète. La localisation française est l’hypothèse pédagogique de calcul.

E(kWh) = puissance supposée(W) × durée mesurée(s) / 3 600 000. CO₂e direct(g) = E × 20. PUE = 1 pour le périmètre ordinateur seul, sans prétendre connaître le refroidissement du bâtiment. Il n’est appliqué qu’une fois. Les trois gardes sont incluses dans les dix tentatives. L’estimation par succès divise par le nombre de contrats réussis, pas par les dix tentatives. Chargement, entraînement, fabrication, réseau et émissions amont exclus. Les résultats restent des calculs conditionnels ; ils ne constituent pas un bilan réel du service. Les anciens scénarios entièrement fictifs sont conservés séparément.

## Éthique, traces et responsabilités
| Risque | Test / preuve | Résultat et réduction | Responsabilité fonctionnelle |
|---|---|---|---|
| Invention sur source absente | TP04 T07, traces des quatre stratégies | PASS de la garde, zéro appel ; aucune réponse factuelle inventée | Validateur et analyste |
| Contradiction de sources | T08 avec métadonnée de conflit explicite | PASS de refus déterministe ; pas de résolution documentaire générale | Contrôle de provenance |
| Injection dans une note | T09, sorties LLM conservées | A échoue, B/routing/cascade réussissent ce cas dans la confirmation ; contrôle et revue restent requis | Orchestrateur et analyste |
| Demande sensible ou action bancaire | T10 et tests API action interdite | Refus déterministe ; aucune action bancaire disponible | API et responsable de démonstration |
| Rétention et données dans les logs | Test minimisation des traces et sauvegarde/restauration | Journal de service sans prompt ni texte libre ; références de prédiction hachées ; purge après 30 jours | Responsable technique à désigner |
| Biais de couverture | Variables PCA, deux jours, peu de fraudes, pas d’attributs protégés exploitables | Aucune équité démographique démontrée ; usage limité au benchmark | Groupe et futur référent métier |

La validité de JSON est un contrôle formel. Un PASS n’est pas une certification de sûreté, ni de résistance générale aux injections. Le hachage d’une référence ne garantit pas l’anonymat. Les traces de benchmark sont fictives, les données brutes et SQLite restent hors dépôt. Les mesures bancaires et les contributions humaines ne sont pas inventées.

## Décision
GO pour démonstration locale surveillée, NO-GO pour usage bancaire autonome. La cascade n’est pas promue. Les TP08 documentent la charge et la reprise. Une qualification juridique et organisationnelle spécialisée serait nécessaire pour un vrai déploiement ; aucune conformité RGPD/AI Act n’est annoncée.

## Reproduction
python src/benchmark_tp04.py --output experiments/results/tp04_reproduction ; python tests/check_orchestrator.py ; python src/green_estimate.py. Les tableaux TP05 renvoient aux traces TP04 existantes. L’audit historique du jeu V2 reste dans tp05_mesures_v2_historique.csv. Les comparaisons n’agrègent pas les workloads 10/12.
