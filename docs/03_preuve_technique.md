# Première preuve technique C3 — expérience exécutée

## Hypothèse et système
Hypothèse exploratoire : une diffusion gaussienne de transactions étiquetées fraude peut produire des exemples utilisables pour augmenter l'entraînement d'un détecteur. La valeur métier reste à démontrer.
Jeu OpenML 1597, version 1, empreinte vérifiée. Train de 170 235 transactions dont 342 fraudes ; validation de 56 745 dont 57 fraudes. Test final non évalué lors de cette première preuve. L’évaluation ultérieure figure dans docs/06_resultats_et_decisions.md.

## Expérience et configuration
29 entrées, V1 à V28 et log1p(Amount). Time exclu du détecteur ; il sert à la séparation temporelle. Normalisation du détecteur ajustée sur train. Régression logistique, C=1, max_iter=2000. Comparaisons avec données originales, pondération des classes et rééchantillonnage aléatoire apparié au nombre de synthétiques acceptés.
DDPM gaussien inconditionnel appris sur la classe fraude, MLP 128–128, 100 pas, schedule bêta linéaire 0,0001 à 0,15, Adam 0,001 et 2 000 mises à jour. 20 % des fraudes de train sont réservées au contrôle interne du débruitage ; scaler du générateur ajusté uniquement sur le sous-ensemble interne d'apprentissage. Trois seeds 17, 42 et 73. Ratios d'ajout visés de 1 et 4 exemples par fraude de train. Modèle pédagogique simple, distinct d'une reproduction complète de TabDDPM.

## Résultats mesurés / calculés
| Configuration | AP moyenne | Écart-type seeds |
|---|---|---|
| B1_class_weight | 0.7532 | 0.0000 |
| B2_random_over_x4 | 0.7088 | 0.0053 |
| B2_random_over_x1 | 0.6934 | 0.0174 |
| G1_ddpm_x4 | 0.6836 | 0.0442 |
| G1_ddpm_x1 | 0.6720 | 0.0261 |
| B0_original | 0.6236 | 0.0000 |

Les moyennes et écarts-types sont calculés à partir des mesures sauvegardées. La dispersion nulle des références logistiques traduit un ajustement déterministe avec ce solveur ; elle ne démontre pas une absence d'incertitude statistique.
La MSE moyenne de prédiction du bruit sur les dix cas internes de seed 42 passe de 0.9919 pour la prédiction de bruit nul à 0.3120 pour le réseau appris. Cette mesure porte sur dix niveaux de bruit, sans intervalle de confiance, et ne mesure pas la qualité métier.

## Incident reproductible et risque
Des sorties ont un log-montant négatif. Seed 42, ratio x4 : 71 sorties rejetées sur 1 368. Le filtre est explicite et le baseline de rééchantillonnage reçoit le même nombre d'ajouts acceptés. Les sorties sont conservées dans l'espace log1p pour éviter une conversion implicite.
Hypothèse de correction : une représentation du montant à support adapté pourrait réduire les rejets. Toute nouvelle comparaison sera séparée de cette expérience.
Aucun quasi-doublon au seuil standardisé 1e-6 n'a été observé parmi les générations acceptées ; cela ne prouve pas la confidentialité ni l'absence de mémorisation.

## Décision
La pondération des classes domine cette première comparaison. La diffusion améliore la référence originale en moyenne mais ne justifie pas son remplacement. Conserver la référence pondérée pour le prototype et poursuivre l'analyse du générateur si les ressources le permettent. Ne pas annoncer de gain opérationnel ni d'économies financières.

## Reproduction et preuves
Depuis la racine du projet, installer requirements.txt, puis exécuter `python src/audit_data.py` et `python src/run_experiment.py`. Config figée dans configs/experiment_v1.json ; résultats et artefacts dans experiments/v1 ; dix cas C3 dans tests/cases.csv et leur trace JSON. Les seeds, versions et matériel logiciel figurent dans run_metadata.json. Responsables à renseigner avec l'équipe.
La longueur de 1 à 2 pages devra être vérifiée après mise en page du rendu.
