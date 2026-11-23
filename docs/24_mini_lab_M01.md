# TP M01 — comparaison de deux petits LLM
Équipe Ahmed, Meriem, Flavio. Mini-lab distinct du projet final, réalisé sur douze nouvelles tâches construites : quatre extractions, quatre raisonnements et quatre synthèses. Jeu, prompts et grille sauvegardés avant les appels dans experiments/m01. Aucune donnée client réelle. Deux modèles exacts identiques au projet, mêmes prompts, décodage glouton, plafond 100 tokens, CPU après warm-up.

| role | cases | passes | extraction | reasoning | synthesis | latency_p50 | latency_p95 |
|---|---|---|---|---|---|---|---|
| verifier | 12 | 3 | 0.000 | 0.000 | 0.750 | 0.880 | 1.279 |
| writer | 12 | 3 | 0.000 | 0.000 | 0.750 | 0.833 | 1.281 |

Qualité automatique : JSON exact pour extraction/raisonnement, couverture lexicale de quelques points pour synthèse. Une paraphrase correcte peut être pénalisée et une réponse incorrecte peut contenir les mots attendus. Il ne s’agit pas d’une évaluation sémantique humaine. Les erreurs d’extraction incluent des clés ajoutées ; deux abstentions de raisonnement sont formulées en texte plutôt qu’au format demandé. Ce sont des erreurs de contrat, distinctes d’une incapacité à identifier le bon sens de l’action.

Seuil de choix figé : au moins 75 % globalement et 50 % dans chaque catégorie. Les deux modèles obtiennent 3/12 au contrôle automatique ; **aucun n’est retenu selon cette grille**. Le coût API est nul ; coût matériel, énergie et coût complet par succès ND. Appels : 12 par modèle, sans retry. Temps de chargement exclu.

Deux limites majeures : douze tâches construites ne représentent pas tous les usages ; la métrique lexicale de synthèse nécessite relecture humaine. La décision ne s’étend pas à la qualité générale de ces modèles. Question pour la suite : un routeur par catégorie pourrait-il réduire les erreurs sans multiplier les appels ? Annotation humaine et contributions réelles à compléter. Reproduction : python src/benchmark_m01.py dans une copie neuve ; les fichiers existants sont protégés.
