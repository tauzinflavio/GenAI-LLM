# Suivi consolidé des exigences et preuves
État du 23 novembre 2026. Les documents de cours définissent des critères pédagogiques ; ils ne donnent pas une permission de publier des données ou d’agir sur un système bancaire.

| Exigence | Statut et preuve |
|---|---|
| C2 note 3–5 pages, métier, alternatives, schéma, ROI, 2 hypothèses | Réalisé : deliverables/C2_Cadrage_FraudLab.pdf, 5 pages ; hypothèses explicites, scénarios autorisés |
| C3 preuve 1–2 pages, cas, baseline, échec, trace | Réalisé : deliverables/C3_Preuve_technique_FraudLab.pdf, 2 pages ; tests/cases.csv et denoising_trace.json ; experiments/results.csv |
| J1 diffusion, deux configurations, baseline et métriques | Réalisé : experiments/v1, final_test ; ratios x1/x4, trois seeds ; décision négative documentée |
| Fidélité, diversité et risques | Réalisé de façon descriptive : generation_quality.csv, tests proximité/rejets ; pas de garantie de confidentialité |
| Front, API, persistance | Réalisé : app/index.html, src/app.py, SQLite local exclu du partage |
| TP03 POC V1 et plan V2 | Réalisé : docs/04_poc_v1_plan_v2.md, llm_v1 et llm_v2 |
| TP04 deux modèles, routing/cascade, 10 cas et limites | Réalisé : src/orchestrator.py ; test_cases.jsonl ; résultats TP04 et tests de robustesse ; incidents conservés |
| TP05 coût/succès et levier | Réalisé au statut disponible : mesures de ressources et appels ; API 0 €, coût complet réel ND |
| Green énergie/PUE/CO₂e et limites | Calcul conditionnel disponible, facteur historique RTE sourcé ; puissance réelle non mesurée ; aucune empreinte réelle annoncée |
| Éthique ≥3 risques et traces | Réalisé : TP05, source absente/conflit/injection/sensibilité, refus API, minimisation des logs |
| TP08 décision, service réel, deux paliers, panne/reprise | Réalisé : deployment_decision.md ; smoke.json ; outputs/load_* ; incident.json ; incident_runbook.md |
| Mini-lab M01 indépendant 4/4/4 | Exécution réalisée : experiments/m01 ; fiche PDF 1 page ; annotation humaine attendue |
| Mini-défi diffusion papier/code officiel | Lecture réalisée au commit figé : docs/22_mini_defi_diffusion.md ; aucune exécution officielle revendiquée |
| Reproduction | Environnement neuf sur le même Mac, 18 scores reproduits ; limites dans docs/19_verification_et_reproduction.md |
| Groupe et responsabilités | Membres confirmés ; interlocuteur et contributions réelles à renseigner |
| Validation humaine | À effectuer par le groupe ; grilles conservées, non remplacées par le vérificateur LLM |
| Soutenance / PowerPoint | Reporté explicitement par l’utilisateur |
| Git commun et commit | Publié et vérifié sur tauzinflavio/GenAI-LLM ; commit et contrôle des 181 fichiers dans docs/27_publication_github.md |

Les branches RAG documentaire et agent-outils sont des options du C3. Notre périmètre retient diffusion et rapports LLM factuels ; aucun index RAG ou agent agissant sur des comptes n’est annoncé. Les dates de séance ne valent pas dates de remise. La grille individuelle des cours reste distincte du travail collectif fourni.


Mise à jour GitHub : import autorisé le 23 novembre 2026 dans https://github.com/tauzinflavio/GenAI-LLM ; la publication est terminée et sa vérification consignée dans docs/27_publication_github.md.
