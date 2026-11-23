# Green AI et coût — périmètre de la première preuve

## Mesures disponibles
Les durées d’apprentissage et de sampling DDPM figurent dans experiments/v1/generation_metrics.csv. Les durées de fit et d’inférence des détecteurs figurent dans experiments/v1/metrics.csv. Les temps CPU observés des LLM, tokens, appels et p95 figurent dans experiments/llm_v1. Pour A+B, la durée comprend les deux appels. Les chargements sont enregistrés séparément et exclus des latences de benchmark. Les appels sont locaux et n’entraînent aucun coût API facturé.

Le prix du matériel, son amortissement, l’électricité et la supervision ne sont pas chiffrés. Un coût API nul ne signifie pas un coût d’exploitation nul.

## Énergie et CO₂e à estimer
Aucune mesure électrique directe n’a été réalisée. La puissance moyenne, le facteur carbone et le PUE ne sont pas connus. Le dashboard permet de saisir ces hypothèses et de calculer un scénario, sans préremplir des valeurs non sourcées.

Énergie (kWh) = durée (s) × puissance supposée (W) × PUE / 3 600 000.
CO₂e (g) = énergie (kWh) × facteur carbone (gCO₂e/kWh).

Si la puissance est mesurée à la prise pour l’ensemble du poste, ne pas appliquer deux fois un surcoût d’infrastructure déjà compris. Le PUE d’un datacenter ne doit pas être transposé au poste local sans justification. Pour un poste local, préciser les consommations incluses dans la mesure ou l’hypothèse.

Un scénario fondé sur la durée seule ignore la variation de puissance selon la charge, le chargement des poids, le téléchargement, l’inactivité et la fabrication. Les présenter comme exclus du périmètre quand ils le sont. Les comparaisons par dossier doivent fixer la même unité fonctionnelle et un niveau de qualité acceptable. Les faibles taux de conformité des LLM limitent toute conclusion d’efficience utile.

## Travail restant
Identifier une source de puissance ou réaliser une mesure, sourcer le facteur carbone, définir le périmètre, renseigner les incertitudes et comparer des configurations satisfaisant le critère de qualité. Présenter un intervalle ou plusieurs scénarios justifiés. Les valeurs carbone restent « non mesurées » à ce stade.

## Scénarios pédagogiques disponibles
Les calculs de sensibilité autorisés sont dans docs/15_scenarios_green_ai.md et experiments/green_ai_scenarios.csv. Les paramètres restent hypothétiques et ne remplacent pas les mesures décrites ci-dessus.
