# Suivi final des TP et du projet commun
Version du 23 novembre 2026. Périmètre confirmé par le groupe : TP et projet final commun, hors soutenance et PowerPoint. Les exercices de révision, informations de cours et lectures complémentaires ne sont pas des blocages du rendu sans consigne spécifique de remise.

| Bloc | Réalisation et preuve | Statut exact |
|---|---|---|
| TP01 | notebooks/TP01_FraudLab.ipynb ; experiments/tp01/execution.json ; 4figures | Exécuté, assertions réussies, conclusions et lien fraude |
| TP02 | notebooks/TP02_FraudLab.ipynb ; experiments/tp02/execution.json ; 1figure | Exécuté, assertions réussies, diagnostic et réflexion |
| C2 | deliverables/C2_Cadrage_FraudLab.pdf ; 29_couts_et_processus_detail.md | 5pages, schéma, AS IS/TO BE, alternatives, ROI et coûts hypothétiques détaillés |
| C3 | deliverables/C3_Preuve_technique_FraudLab.pdf ; tests/cases.csv et denoising_trace.json | 2pages, 10cas, baseline, incident et décision |
| J1 diffusion | experiments/v1 et final_test ; docs/25_qualite_generation.md | DDPM réel, x1/x4, trois seeds, baselines, métriques et incertitude |
| TP03 | docs/04_poc_v1_plan_v2.md ; experiments/llm_v1 et llm_v2 | Générations réelles, prompt et incident, schémas V1/V2 |
| TP04 | src/orchestrator.py ; experiments/results/tp04 | Mono-A/B, routing/cascade, mêmes10cas, 40essais ; jugements humains non remplis |
| TP05 | docs/06_tp05_finops_green_ethique.md ; tp05_mesures.csv et tp05_green_estimates.csv | Coûts disponibles, ND réels, calculs conditionnels, optimisations et risques |
| TP08 | deployment_decision.md ; evidence/ ; outputs/load_c1 et load_c3 | Vraie inférence, deux charges, incident/reprise et restauration ; ADR1page présent |
| M01 | experiments/m01 ; deliverables/TPM01_Comparaison_FraudLab.pdf | 12tâches 4/4/4 ; fiche1page ; relecture humaine attendue |
| POC commun | app/index.html ; src/app.py ; /review | 7écrans, ressources, FinOps et atelier de relecture |
| Fiche modèle | docs/MODEL_CARD.md | Usage, données, métriques, versions, risques, ressources et limites |
| Reproduction | README ; scripts/check_package.py ; tests/ | Commandes, environnement, preuves ; test final archivé non réoptimisé |
| Groupe | configs/team.json | Ahmed/Meriem/Flavio ; interlocuteur, opérateur et contributions **restent à décider** (confirmation explicite) |
| Jugement humain | /review ; deliverables/Relecture_LLM.html ; scripts/import_human_reviews.py | 158sorties préparées en aveugle ; **aucune annotation humaine inventée** |
| Soutenance / PPT | Hors préparation actuelle | Exclus à la demande du groupe |

## Conditions humaines qui ne peuvent pas être certifiées par l’assistant
Le groupe doit lire/noter les sorties, désigner l’interlocuteur et les contributions réelles, vérifier les modalités de remise et le format binôme/trinôme de M01. Ces points ne sont pas déclarés accomplis par la simple présence d’une grille ou d’un PDF. Le rôle d’opérateur de séance est défini dans le runbook ; sa désignation nominative reste à décider.

## Statut scientifique
Les expériences existantes restent exploratoires. Une absence de gain ne signifie pas un TP non réalisé. Les objectifs chiffrés prospectifs sont dans configs/confirmation_future.json et n’ont pas été appliqués rétroactivement. Coût API nul n’est pas coût complet nul ; énergie réelle ND et estimations séparées. Aucun usage bancaire autonome autorisé.

## Dépôt et sources
Un seul dépôt : https://github.com/tauzinflavio/GenAI-LLM. Les notebooks de réalisation ne redistribuent pas intégralement les supports. Les données, poids, SQLite, sauvegardes et secrets restent hors partage. Les anciens brouillons sont conservés dans archive/ avec liens vers les documents courants.
