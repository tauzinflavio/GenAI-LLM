# Démonstration et vérification

## Parcours conseillé
1. Vue d’ensemble, provenance et métriques de validation.
2. Analyse d’alertes, choix d’une transaction de validation et calcul du score.
3. Référence déterministe puis mono-LLM et Multi-LLM. Montrer un échec de contrat et son signalement.
4. Enregistrer un avis et le retrouver dans le journal.
5. Générer quatre échantillons avec seed 42, lire le nombre de rejets et le temps.
6. Évaluation, comparer validation et test final, expliquer le choix figé et l’incertitude.
7. Impact et ROI, saisir uniquement des hypothèses justifiées et identifier les résultats comme scénarios.

## Limites de la version
Le rapport LLM est une preuve de génération structurée et de vérification factuelle. L’interprétation bancaire avancée est limitée par les composantes PCA. Le POC n’intègre pas de RAG ni d’agent, car ces composants ne sont pas nécessaires à cette architecture. Le parcours ne réalise aucune opération bancaire.

La persistance fonctionne dans data/local_app.sqlite. Les événements des vérifications sont identifiables comme activité locale de contrôle. La base reste hors archive de partage.
