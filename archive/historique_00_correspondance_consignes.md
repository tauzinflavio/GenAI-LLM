État initial conservé pour traçabilité. Pour l’avancement actualisé, consulter docs/08_suivi_exigences.md.

# Articulation des consignes ECE

## Références conservées
- Projet_final_ECE_Pack_ETUDIANTS_COMPLET.pdf, version du 3 novembre 2026. Cadre des deux jalons et cadrage C2.
- ECE_MSc2_Projet_Final_Sujet_C3_60min_LLM_RAG_Agent_Diffusion.pdf, daté du 14 novembre 2026. Première preuve technique et livrables C3.
- 03_TP_POC_GenAI_MultiLLM.pdf, daté du 16 novembre 2026. Consolidation V1 et préparation V2, déjà utilisé dans le plan.

## Correspondance avec notre sujet
| Exigence | Application fraude bancaire | État et preuve |
|---|---|---|
| C2, cadrage 3 à 5 pages, schéma et ROI | Besoin analyste, diffusion et synthèses | Brouillon docs/02_cadrage.md ; ROI à renseigner |
| Données autorisées et traçables | OpenML 1597 version 1 | data/manifest.md et audit |
| 8 à 10 cas C3, attendu et vérification | Scénarios détection / génération / refus | Dix scénarios proposés, entrées encore à instancier |
| Chaîne minimale générative | Première expérience diffusion tabulaire | À implémenter ; audit seul insuffisant pour valider C3 |
| Baseline sur mêmes entrées | Comparaison explicite et métrique adaptée | Protocole préparé, non exécuté |
| Échec, risque et hypothèse de correction | Validité, mémorisation, cas hors périmètre | Risques documentés ; incident expérimental à produire |
| docs/03_preuve_technique.md, 1 à 2 pages | Résultat, erreur et décision | Trame préparée, résultat non mesuré |
| tests/cases.csv ou .json | Cas avec données et méthode de contrôle | experiments/test_cases.jsonl existant ; export au format C3 à produire après instanciation |
| experiments/results.csv et trace | Résultats statutés et configurations | Registre présent ; audit séparé, aucun résultat génératif |
| README, trace et responsables | Reproduction et prochaine expérience | README actualisé ; responsables à attribuer |
| J1, expérimentation diffusion et POC complet | Augmentation puis interface/API/stockage | À développer |
| J2, mono contre Multi-LLM et Green AI | Rédacteur et vérificateur | À développer et comparer |

Le dossier partagé actuel prépare le dépôt unique. Aucun commit Git n'est revendiqué. Les dates figurant sur les supports identifient les séances et les versions ; les échéances finales restent à confirmer.

## Prochaine progression
1. Instancier les cas C3 à partir de données autorisées et identifier au moins deux cas difficiles.
2. Réaliser une première preuve diffusion, par exemple q_sample documenté. Ce bruitage constitue une preuve partielle et ne démontre pas un générateur entraîné ni une amélioration de détection.
3. Exécuter la baseline pertinente sur les mêmes entrées et consigner la métrique.
4. Conserver paramètres, temps, sortie et échec ; compléter la preuve C3.
5. Entraîner le générateur et le détecteur puis construire le POC final.
