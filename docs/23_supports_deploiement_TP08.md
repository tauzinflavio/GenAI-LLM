# Supports de déploiement reçus le 23 novembre
Le cours ECE_M2_DEPLOIEMENT_ARCHITECTURES_ALIGNEMENT_FINAL et le TP08 complètent le même projet. Le scénario des 350 agents et les prix du cours sont des exemples pédagogiques, pas des exigences de notre application bancaire.

Le TP08 autorise l’adaptation de l’API existante. FraudLab utilise donc FastAPI et ses processus Transformers locaux, sans remplacer le moteur par Ollama ni acheter de GPU cloud. Les preuves obligatoires sont une décision d’architecture, un état vivant/prêt distinct, une inférence réelle avec trace_id, deux paliers de charge, une panne avec reprise et un runbook. Elles sont référencées dans docs/deployment_decision.md.

Le TP08 ne remplace ni l’expérimentation diffusion ni les comparaisons TP04/TP05. Le dépôt Git commun est publié sur tauzinflavio/GenAI-LLM ; les mises à jour conservent les preuves antérieures. Les dates de séance ne valent pas dates de remise.
