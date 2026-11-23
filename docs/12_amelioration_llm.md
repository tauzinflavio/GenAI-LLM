# Expérience de prompt V2 et confirmation séparée

## Protocole
Le premier benchmark à dix cas a révélé des erreurs de schéma et de respect des faits. Une variante de prompt à quatre exemples explicites a été écrite puis figée dans configs/prompts/report_v2.txt. Aucun réglage supplémentaire n’a été choisi à partir des résultats ci-dessous.

Quatre cas du premier jeu sont utilisés comme contrôle de développement. Douze nouveaux cas fictifs distincts forment le jeu séparé. Les prompts V1 et V2 sont évalués sur ces mêmes douze cas pour comparer leurs résultats. Le protocole, les cas et le hash du prompt figurent dans frozen_protocol.json, écrit avant les inférences de confirmation.

Les modèles, révisions, plafond de 100 tokens, CPU et décodage greedy sont conservés. A désigne SmolLM2-360M-Instruct et B Qwen2.5-0.5B-Instruct. Le changement de prompt augmente sa longueur ; les tokens et le temps sont donc mesurés plutôt que supposés constants. La chaîne A+B utilise le même prompt de version donnée pour son rédacteur et son vérificateur.

## Résultats sur les douze cas séparés

| Configuration | Contrats stricts | Latence p95 | Tokens entrée cumulés |
|---|---|---|---|
| v1_A_mono | 1 / 12 | 1.967 s | 1798 |
| v1_A_plus_B | 5 / 12 | 4.180 s | 4125 |
| v2_A_mono | 2 / 12 | 2.363 s | 4570 |
| v2_A_plus_B | 1 / 12 | 6.475 s | 9446 |
| v2_B_mono | 8 / 12 | 1.659 s | 4229 |

Les contrôles stricts portent sur le JSON, les quatre clés, le montant, le score, le pays et la règle d’action. Un score de 8/12 correspond à la réussite de ce contrat sur douze fixtures ; il ne représente pas une précision de détection bancaire.

## Analyse des erreurs
Le petit modèle A reprend parfois le pays et l’action du dernier exemple au lieu de ceux du dossier. La chaîne V2 peut copier un brouillon erroné ou reproduire les délimiteurs FACTS/DRAFT. Une instruction plus longue ou illustrée peut donc dégrader certains modèles. Les sorties brutes permettent de retrouver ces échecs.

B seul avec le prompt V2 obtient le meilleur résultat descriptif de cette expérience. Le même prompt dégrade fortement A+B. Les résultats ne justifient donc pas l’adoption du Multi-LLM pour ce contrat de copie factuelle. L’intérêt d’un LLM doit aussi être comparé au rapport déterministe, déjà disponible dans le POC.

## Décision et portée
Conserver le rapport déterministe comme défaut de l’application. Préserver les modes LLM V1 pour la démonstration de leurs limites et montrer séparément les résultats V2. Le nouveau prompt n’est pas activé automatiquement dans les rapports de l’application. Son éventuelle adoption nécessitera un nouveau jeu indépendant ou un protocole préenregistré, car les résultats de ce jeu séparé sont désormais connus.

La présente étude évalue des contrats formels sur des cas fictifs construits. Le nombre de cas est faible, le p95 est descriptif et une annotation humaine est toujours attendue. Aucun résultat de détection ou modèle de diffusion n’a été réentraîné à partir de cette expérience.

## Reproduction
Exécuter src/improve_llm.py dans une copie de travail avec les poids locaux disponibles. Le script refuse de remplacer son résumé si une évaluation terminée existe. Les sorties et paramètres se trouvent dans experiments/llm_v2. Compléter human_review.csv en suivant docs/10_grille_annotation_humaine.md.
