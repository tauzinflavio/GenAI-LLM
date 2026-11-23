# TP04 — comparaison exécutée et confirmée
La campagne finale se trouve dans experiments/results/tp04, copie identique de tp04_confirmation. Le protocole est enregistré avant ses appels avec empreintes du code, des modèles, du prompt et du workload. Dix mêmes fixtures : quatre usuelles, deux complexes, source absente, contradiction, injection, demande sensible. Ordre des stratégies tournant par cas. Warm-up et chargement exclus. Aucun autre benchmark ni démarrage de modèle n’a été lancé pendant cette confirmation.

| strategy | cases | passes | model_passes | guard_cases | calls | latency_p50 | latency_p95 |
|---|---|---|---|---|---|---|---|
| cascade | 10 | 9 | 6 | 3 | 12 | 2.806 | 4.120 |
| mono_a | 10 | 5 | 2 | 3 | 7 | 1.914 | 3.595 |
| mono_b | 10 | 9 | 6 | 3 | 7 | 1.531 | 1.866 |
| routing | 10 | 7 | 4 | 3 | 7 | 1.616 | 1.982 |

Les trois gardes identiques aux quatre stratégies refusent les sources absentes, contradictions déclarées et demandes sensibles ; ce ne sont pas des succès de génération. B et cascade réussissent donc 6/7 cas soumis aux modèles, auxquels s’ajoutent 3 refus déterministes, soit 9/10. Le montant nul T03 reste un échec pour toutes les stratégies. Le cas d’injection T09 réussit avec B, routing et cascade et échoue avec A ; un seul cas ne prouve pas une résistance générale.

La cascade répare des échecs de A mais utilise 12 appels contre 7 pour B seul sans gain de conformité. NO-GO pour promouvoir automatiquement la cascade. Le rapport déterministe reste le défaut applicatif. B est le meilleur candidat local parmi ces stratégies sur ce contrat, sans preuve d’expertise bancaire ni validation humaine.

## Incident de la première campagne et correction
La campagne initiale est conservée dans tp04_initial. Un timeout de B sur T09 l’avait arrêté. Les stratégies suivantes héritaient de cette indisponibilité, ce qui mélangeait comportement du modèle et panne de backend ; une partie du benchmark avait aussi chevauché le chargement d’une autre instance. Elle reste une preuve d’incident, pas le tableau final de qualité comparative.

La confirmation conserve les mêmes modèles, prompt et cas, et vérifie/rétablit l’état des workers avant chaque stratégie. Le délai de rétablissement préalable est consigné séparément et exclu de la latence d’inférence. Aucun changement de prompt n’est choisi à partir de cette répétition. Le succès T09 de B dans la confirmation ne contredit pas le timeout observé dans la première campagne. Cette répétition est motivée par la correction de l’isolation des stratégies ; ce n’est pas un nouveau test indépendant.

## Limites et reproduction
p95 descriptif sur dix cas, dont trois gardes quasi immédiates, sans intervalle de confiance. Mac M2 / 8 Go, machine non réservée exclusivement à l’expérience. Une validation de performance exigerait une charge contrôlée et davantage de répétitions. TTFT/TPOT ND, sortie non streamée. Annotation humaine attendue. Les 14 tests de contrôle simulés dans tp04_robustness.json prouvent limites et refus, pas la qualité de vrais modèles.

python src/benchmark_tp04.py --output experiments/results/tp04_reproduction, puis python tests/check_orchestrator.py. La campagne existante n’est pas écrasée.
