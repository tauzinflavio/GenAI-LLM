# Trame proposée pour la soutenance

Le nombre de diapositives et la durée seront ajustés aux modalités de l’enseignant. Cette trame prépare le contenu ; les diapositives finales restent à produire.

## 1. Besoin et périmètre
Présenter l’analyste, le traitement des alertes et le caractère pédagogique du scénario. Définir les deux questions, utilité de la diffusion et apport des LLM.

## 2. Alternatives et architecture
Montrer le détecteur simple, le rééquilibrage, la diffusion puis le rédacteur et le vérificateur. Séparer apprentissage hors ligne et application. Montrer le rôle de la revue humaine.

## 3. Données et protocole
Présenter source, audit, labels, partitions et absence de fuite dans les transformations apprises. Expliquer les limites des variables PCA et de la fenêtre temporelle.

## 4. Modèle de diffusion
Illustrer bruitage, prédiction du bruit et génération inverse. Expliquer les 29 variables, le log-montant, le MLP, les seeds et les rejets. Relier les choix à l’analyse des articles sans revendiquer une reproduction intégrale de TabDDPM.

## 5. Résultats de détection
Utiliser la figure de validation et les résultats du test final. Expliquer la décision figée et l’intervalle d’incertitude. Conserver le résultat négatif sur la supériorité de la diffusion.

## 6. Mono-LLM et Multi-LLM
Présenter les deux modèles, le contrat factuel, les cas difficiles et la comparaison à entrées identiques. Montrer une sortie correcte et une erreur. Distinguer évaluation automatique et annotation humaine.

## 7. Application et démonstration
Calculer un score sur validation, produire un rapport, afficher un contrôle, consigner un avis et le retrouver dans le journal. Générer quatre exemples avec le DDPM et consulter les résultats.

## 8. Valeur et impact
Présenter les trois ROI comme scénarios hypothétiques. Expliquer le temps gagné nécessaire à la rentabilité et le coût de la revue. Présenter les durées mesurées et les hypothèses environnementales avec leurs exclusions.

## 9. Décision et limites
Expliquer le choix du détecteur retenu, du rapport déterministe par défaut et des prochaines validations nécessaires. Terminer sur les conditions de validité des conclusions et les contributions de chaque membre.

## Questions à préparer
- Pourquoi générer des données si une pondération simple fonctionne bien ?
- Quelle différence entre une perte de bruit faible et une bonne utilité aval ?
- Pourquoi conserver le test final à l’écart du choix des configurations ?
- Pourquoi un second LLM peut-il dégrader une réponse ?
- Quelle preuve permet d’annoncer une économie métier ou un gain carbone ?
- Quels résultats pourraient faire changer la décision d’architecture ?
