# FraudLab — fraude bancaire, diffusion et Multi-LLM
Ahmed · Meriem · Flavio — ECE MSc2 IA — préparation de remise du 23 novembre 2026.

Un seul projet relie le jalon GenAI/Diffusion et le jalon Multi-LLM/Green AI. Scénario métier hypothétique autorisé. Démonstration locale surveillée ; aucune action bancaire. Interlocuteur principal, contributions réelles et échéances de remise à confirmer. Le PowerPoint est reporté à la demande du groupe. Dépôt commun : https://github.com/tauzinflavio/GenAI-LLM. Les étapes à valider par le groupe figurent dans la checklist.

## TP et remise — version finalisée
- [Tableau des TP et livrables](docs/30_matrice_TP_projet_final.md) : périmètre confirmé, sans exercices de révision ajoutés.
- [TP01 exécuté](notebooks/TP01_FraudLab.ipynb) et [TP02 exécuté](notebooks/TP02_FraudLab.ipynb), avec figures et sorties.
- [Synthèse des deux TP](deliverables/TP01_TP02_Synthese_FraudLab.pdf).
- [Architecture et ADR une page](deliverables/Architecture_ADR_FraudLab.pdf) ; [fiche modèle](docs/MODEL_CARD.md).
- [Coûts et processus détaillés](docs/29_couts_et_processus_detail.md), tous explicitement hypothétiques.
- [Atelier de relecture](deliverables/Relecture_LLM.html) : dans l’application, ouvrir « TP & livrables » puis la relecture. Les 158 sorties sont préparées, mais aucun jugement humain n’est généré.
- [Actions restant au groupe](docs/31_taches_groupe.md) : annotations, interlocuteur/contributions/opérateur à décider, modalités de remise à confirmer. Soutenance et PowerPoint exclus.

Relancer les TP avec `python scripts/execute_course_notebooks.py`. Ce lanceur exécute vraiment les cellules Python, intègre stdout/figures au format notebook et échoue si une assertion échoue ; il ne dépend pas de Jupyter. Pour les ouvrir dans Jupyter, utiliser un environnement Jupyter séparé si nécessaire.
Recalculer la ventilation avec `python src/complete_financial_scenario.py`. L’allocation hypothétique ne remplace pas les coûts réels ND.
Exporter les notes humaines puis `python scripts/import_human_reviews.py export.csv --dry-run` pour vérifier, puis sans `--dry-run` pour conserver une campagne séparée. Ne jamais présenter des notes automatiques comme humaines.

## Commencer ici
- [Rapport consolidé](docs/16_rapport_consolide.md)
- [Suivi des exigences et preuves](docs/08_suivi_exigences.md)
- [Checklist de remise](docs/17_checklist_remise.md)
- [PDF de remise](deliverables/)
- [Décision de déploiement TP08](docs/deployment_decision.md) et [runbook](docs/incident_runbook.md)

## Installer et lancer
Python **3.14** a été utilisé et vérifié sur Mac Apple M2 / 8 Go. L’installation séparée sur ce même Mac est documentée ; la compatibilité d’une autre machine/plateforme doit être vérifiée. Depuis la racine du projet :

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python src/prepare_demo.py
.venv/bin/python scripts/serve.py --port 8784
```

Ouvrir http://127.0.0.1:8784/. Attendre le chargement des deux modèles. Le lanceur active le service et limite le CPU à quatre threads. Ctrl+C arrête l’instance lancée. Aucun secret API ni achat cloud requis. Les téléchargements initiaux de données et modèles nécessitent un accès réseau ; l’inférence est ensuite locale. Le dossier de partage ne contient ni les données ni les poids (environ 1,6 Go de fichiers de modèles à télécharger, taille disque distincte de la mémoire float32).

Le script prepare_demo télécharge les entrées manquantes, audite les données et reconstruit les artefacts nécessaires. Il conserve le test final existant et ne relance pas tous les benchmarks LLM. Les scripts de téléchargement figent les révisions. Si le réseau ne permet pas les téléchargements, une nouvelle machine ne pourra pas exécuter les modèles ; ce n’est pas une démonstration simulée de remplacement.

## Parcours de démonstration
1. Vue d’ensemble : résultats réels de validation.
2. Analyse d’alertes : sélectionner un cas de validation, calculer le score, produire le rapport déterministe puis comparer les modèles ; consigner un avis pédagogique.
3. Diffusion : générer quatre vecteurs DDPM, vérifier seed, sorties et rejets. Tester une saisie invalide puis corriger.
4. Évaluation : comparer validation, test final figé, prompts et TP04, sans mélanger leurs workloads.
5. Impact & ROI : lire appels/tokens, charge et coûts ND ; charger les trois scénarios ROI ou saisir des hypothèses énergie explicites.
6. Journal : retrouver l’avis et les événements locaux.
7. TP & livrables : télécharger notebooks/rapports et préparer la relecture humaine en aveugle.

Après une indisponibilité, le bouton « Réactiver l’analyse locale » recharge les processus manquants sans rejouer la demande précédente. Le rapport déterministe reste disponible. Le protocole conserve les échecs LLM et les marque comme tels.

## Tests et reproduction
Dans les commandes ci-dessous, `python` désigne le Python de l’environnement activé. Lancer séparément les expériences coûteuses ; elles ne doivent pas chevaucher les tests de performance.

```bash
python tests/check_orchestrator.py
python tests/check_api.py --base-url http://127.0.0.1:8784
python tests/check_service_safety.py --base-url http://127.0.0.1:8784
python scripts/service_checks.py smoke --base-url http://127.0.0.1:8784
python scripts/service_checks.py load --base-url http://127.0.0.1:8784 --concurrency 1 --requests 12
python scripts/service_checks.py load --base-url http://127.0.0.1:8784 --concurrency 3 --requests 18
python scripts/incident_test.py
python scripts/backup_db.py --check
```

Les preuves de charge et sauvegardes existantes ne sont pas écrasées. Pour refaire une campagne, utiliser une copie neuve ou archiver la précédente. Le test d’incident crée sa seule instance jetable sur 8781 ; ne pas y lancer un autre service. Les doubles de test d’orchestration prouvent des limites de contrôle, pas la qualité de vrais modèles.

```bash
python src/download_data.py
python src/audit_data.py
python src/run_experiment.py
python src/download_llms.py
python src/benchmark_tp04.py --output experiments/results/tp04_reproduction
python src/green_estimate.py
python src/evaluate_generation_quality.py
```

Ne pas relancer le test final pour ajuster les choix. `src/evaluate_final.py` refuse une seconde évaluation si son fichier existe. Pour une reproduction scientifique, travailler dans une copie distincte et conserver les décisions figées. Les benchmarks V1/V2 et M01 conservent leur protocole et leurs scripts propres. L’analyse du dépôt TabDDPM est une lecture au commit figé ; aucune exécution du dépôt officiel n’est revendiquée.

## Résultats et limites
La diffusion n’a pas démontré sa supériorité statistique sur la référence pondérée. Les LLM restent insuffisants sur les contrats et doivent être contrôlés. Le coût API nul n’est pas un coût complet nul. Énergie et carbone réels ND ; calculs conditionnels séparés. À concurrence 3, les rejets de capacité abaissent le p95 global : ce n’est pas une accélération de l’inférence.

L’accès analyste est simulé. Le serveur doit rester sur 127.0.0.1 ; pas de SSO/TLS ou disponibilité de production. La référence libre est hachée avant stockage ; cela ne garantit pas l’anonymat. Rétention locale 30 jours. Les sorties ne doivent pas être utilisées pour prendre une décision bancaire réelle.

## Dossier partagé sur GitHub
`src/`, `scripts/`, `tests/`, `configs/`, `docs/`, `deliverables/`, `experiments/`, `evidence/`, `outputs/` et les manifestes de `data/` composent le dossier de partage. `models/`, données brutes/indices, fichiers binaires d’entraînement, SQLite/sauvegardes, secrets et caches sont exclus. Les supports ECE sont référencés avec empreintes et ne sont pas redistribués.

Le dépôt inclut un manifeste SHA256 des fichiers partagés. Les commits identifient les versions publiées. Les contributions réelles restent à renseigner par le groupe. Les PDF pédagogiques source et les données publiques brutes ne sont pas ajoutés au dépôt.

## Outils et maquette conservés
Les générateurs PDF sont dans tools/, avec requirements-reports.txt. La simulation visuelle initiale est archivée dans archive/ et ne constitue pas un résultat mesuré. L’application réelle se trouve dans app/ et src/.
