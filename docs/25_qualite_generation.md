# Fidélité et diversité des sorties DDPM
Analyse complémentaire descriptive du 23 novembre 2026. Les sorties générées antérieurement sont évaluées sans réentraînement ni nouvel accès au test final. Chaque seed reconstruit exactement son holdout interne de 68 fraudes, exclu de l’apprentissage de son générateur. La normalisation conservée est celle du train interne du générateur.

Le script src/evaluate_generation_quality.py calcule KS et Wasserstein par variable, écart absolu moyen de corrélation, unicité exacte, distances entre paires et distances au plus proche train. Les contrôles concernent les seules sorties ayant passé le filtre de montant. Les tailles sont différentes et les corrélations sont instables sur 68 observations. Aucun seuil de qualité n’est introduit après lecture. Une simple absence de copie ne garantit ni confidentialité ni couverture de tous les modes.

seed,multiplier,real_holdout_rows,synthetic_rows,ks_mean,wasserstein_mean,correlation_mae
17,1,68,327,0.1646708351167104,0.2692830980205315,0.172555605763388
17,4,68,1286,0.18236098536588446,0.29333462539224053,0.12586874997952924
42,1,68,326,0.14377667716123896,0.23787542739065165,0.21011127155257497
42,4,68,1297,0.14895585224758023,0.23192029234986167,0.20307861281988904
73,1,68,321,0.14217266023392922,0.27649130006210954,0.11769321618524892
73,4,68,1242,0.1380102432443909,0.2820525258124729,0.1423140690406266

Le tableau lisible complet est dans experiments/results/generation_quality.csv ; le détail par variable dans generation_quality_by_feature.csv. À seed 42 / x4, la distance médiane des paires synthétiques est inférieure à celle du petit holdout réel, ce qui suggère une dispersion plus faible sur cette vue ; ce n’est pas une démonstration générale de mode collapse. Le test d’utilité aval reste la comparaison indépendante des détecteurs. Aucune sélection supplémentaire n’est effectuée sur le test final.
