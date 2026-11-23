# Note C2 — Brouillon initial

## Sujet et problème
Titre proposé : Détection de fraude sur transactions par carte par augmentation de données de diffusion et assistance Multi-LLM à l'analyse des alertes.
Utilisateur cible proposé : analyste chargé d'examiner les alertes. Le mécanisme de fraude couvert sera précisé à partir des labels et de la documentation du jeu retenu.
Questions scientifiques : les transactions synthétiques améliorent-elles la détection sur un test réel indépendant ? Un second LLM améliore-t-il la fidélité des synthèses à coût et latence acceptables ?
Équipe, interlocuteur, matériel et accès aux modèles : à renseigner.

## AS IS — processus métier hypothétique à valider
| Étape | Acteur / outil envisagé | Information | Mesure à obtenir |
|---|---|---|---|
| Enregistrer la transaction | Système transactionnel | Champs autorisés | Volume et fréquence |
| Calculer un score | Règles ou détecteur | Variables disponibles | Temps et erreurs |
| Créer l'alerte | Supervision | Score et seuil | Volume d'alertes |
| Examiner les faits | Analyste | Dossier accessible | Durée d'examen |
| Rechercher les éléments manquants | Analyste | Sources autorisées | Temps et disponibilité |
| Consigner l'analyse | Analyste | Conclusion et preuves | Durée et reprises |
| Valider et journaliser | Responsable habilité | Dossier validé | Coût et erreurs |
Trois irritants à mesurer : charge de fausses alertes, durée d'examen, rareté des fraudes dans l'entraînement. Aucune observation en banque réalisée.

## Alternatives et choix
| Approche | Apport | Limite à tester |
|---|---|---|
| Processus actuel / règles | Référence explicite | Couverture |
| ML sur données originales | Score appris | Classe minoritaire |
| Même ML avec rééquilibrage simple | Alternative économique | Généralisation |
| Même ML avec augmentation par diffusion | Exemples supplémentaires | Utilité, diversité, mémorisation |
| Synthèse mono puis Multi-LLM | Assistance à la lecture | Inventions et surcoût |
Choix proposé : fixer le détecteur pour isoler l'effet de l'augmentation. La qualité des synthèses constitue une seconde tâche évaluée séparément.

## TO BE et architecture
Flux hors ligne : données autorisées → partitions → diffusion entraînée sur train → contrôles synthétiques → augmentation de train → détecteur → évaluation indépendante.
Flux applicatif : analyste → interface → API / validation → détecteur → score et faits → LLM rédacteur → vérificateur en V2 → revue humaine → stockage et audit → affichage.
La génération produit des transactions et des synthèses textuelles. Prévoir une vue des résultats expérimentaux pour montrer l'apport de la diffusion.
Proposition réversible : Python, PyTorch, scikit-learn, Streamlit, FastAPI et SQLite. Modèles précis et versions à choisir après validation des données et ressources.
À spécifier avant intégration : schémas d'entrée/sortie, timeouts, accès simulé ou authentification, erreurs, champs persistés, références de versions et durée de conservation. La relecture et les corrections humaines entrent dans les coûts.

## Données
Le jeu creditcard OpenML 1597 version 1 a été obtenu et audité. La source indique une licence « Public ». Les contrôles et limites figurent dans docs/04_decision_donnees.md et docs/05_audit_donnees.md. Les partitions chronologiques sont proposées pour le benchmark pédagogique.
Si les variables sont anonymisées, limiter les synthèses aux faits interprétables. Toute donnée pédagogique créée pour un test doit être signalée comme telle. La génération synthétique seule ne démontre pas la confidentialité.

## Hypothèses réfutables
H1 valeur : à détecteur et protocole fixés, la diffusion améliore l'average precision d'au moins delta face aux données originales et au rééquilibrage simple sur un test réel indépendant. Delta reste à justifier et figer.
H2 exploitation : le POC respecte une latence p95 inférieure à L et un coût par demande inférieur à C, avec revue humaine documentée. L et C restent à fixer.
H3 proposée pour Multi-LLM : le vérificateur réduit les affirmations non étayées d'au moins epsilon, tout en respectant H2. Epsilon et grille humaine à fixer.

## Business case
Le CSV joint liste les variables sans leur attribuer de valeurs fictives. Compléter chaque hypothèse avec unité et source ou méthode.
Heures économisées/an = volume × minutes gagnées / 60.
Gain net opérationnel = économies brutes + autres gains étayés − revue supplémentaire − nouveaux coûts métier.
Coût année 1 = investissement initial + exploitation annuelle.
ROI année 1 = (gain net opérationnel − coût année 1) / coût année 1 × 100, si le coût est positif.
Construire trois scénarios, pessimiste, central et optimiste, en indiquant les paramètres modifiés. Éviter le double comptage entre gains de temps, baisse de fausses alertes et pertes de fraude évitées. Un gain hors ligne ne démontre pas une économie opérationnelle.

## Risques et contrôles
| Risque | Effet | Test ou mitigation |
|---|---|---|
| Fuite entre partitions | Gain surestimé | Splits avant ajustement, audit doublons |
| Mémorisation | Copie d'exemples | Proximité aux données train |
| Peu de fraudes | Résultats instables | Effectifs, répétitions, incertitudes |
| Synthèses inventées | Analyse erronée | Faits traçables, grille humaine, abstention |
| Variables anonymisées | Portée métier limitée | Restreindre les affirmations |
| Coût / latence | Usage peu viable | Logs et contraintes prédéfinies |
| Licence ou accès | Données inutilisables | Vérification et manifeste |
| API indisponible | Pipeline interrompu | Timeout et erreur contrôlée |

## Références et décisions
Deux pistes scientifiques identifiées : DDPM et TabDDPM, détaillées dans references.md. Lecture complète encore à réaliser.
Décisions ouvertes : données et droits, matériel, modèles, seuils, budget, équipe et échéances. Le dossier C2 devra comprendre cette note complétée, un schéma lisible et les calculs financiers.
