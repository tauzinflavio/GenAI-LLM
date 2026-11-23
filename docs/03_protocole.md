# Protocoles et statut des expériences
Les expériences de diffusion, détection et LLM sont exécutées ; l’ancien plan non exécuté est dans `archive/historique_03_protocole.md`.

- Diffusion : `configs/experiment_v1.json`, `experiments/v1/run_metadata.json`. Deux ratios, trois seeds et mêmes détecteurs/splits. Résultats de validation exploratoires.
- Test final : sélection et seuils dans `experiments/final_test/frozen_decision.json`. Test réel non augmenté ; ne pas le réutiliser pour optimiser.
- Prompt V2 : `experiments/llm_v2/frozen_protocol.json`, nouveaux cas séparés ; références V1 réexécutées sur les mêmes cas de cette expérience.
- TP04 : `experiments/results/tp04/protocol.json`, confirmation isolant les workers ; campagne initiale conservée comme incident. Contrats automatiques, pas annotation humaine.
- M01 : `experiments/m01/protocol.json`, 12 tâches 4/4/4 indépendantes du workload projet.
- TP08 : hypothèse de charge enregistrée avant les paliers, `outputs/load_c1.json` et `load_c3.json` ; incident et reprise dans `evidence/`.
- TP01/TP02 : scénarios de cours synthétiques, notebooks exécutés et assertions ; résultats séparés du benchmark bancaire.

## Confirmation future préparée, non exécutée
`configs/confirmation_future.json` définit avant une éventuelle nouvelle collecte un gain AP minimal, un gain qualité Multi-LLM, p95 et budget. Aucune nouvelle collecte n’a eu lieu ; aucun protocole rétroactif. Si le coût réel reste ND, le critère économique ne peut être déclaré validé.
## Jugement humain
Les grilles restent réservées aux personnes qui relisent réellement les sorties. L’assistant ne se déclare pas annotateur humain. L’atelier `/review` prépare cette tâche en aveugle et permet d’exporter les annotations ; le groupe doit encore le réaliser.
