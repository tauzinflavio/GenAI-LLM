# Avancement du groupe — 23 novembre 2026
Ahmed · Meriem · Flavio. Interlocuteur principal à désigner.

## Réalisé et disponible
- Diffusion tabulaire entraînée, baselines, deux ratios, trois seeds, test final figé, fidélité/diversité et limites.
- Deux vrais LLM locaux, prompts V1/V2, TP03 puis TP04 : modèles seuls, routage, cascade, cas gelés et contrôles bornés.
- Confirmation TP04 : A 5/10, B 9/10, routing 7/10, cascade 9/10 ; chaque total inclut trois gardes déterministes. B et cascade réussissent 6/7 cas d’inférence ; B utilise 7 appels contre 12. Première campagne conservée comme incident.
- TP05 : FinOps, calculs Green conditionnels, risques et traces éthiques. Coût complet et énergie réels non mesurés, sans les confondre avec les hypothèses.
- TP08 : service local, inférence réelle, deux niveaux de charge, panne/reprise et restauration SQLite.
- Mini-lab M01 4/4/4 et étude papier/code officiel au commit documenté.
- Dashboard six écrans, 41 contrôles automatiques réussis, revue à 320 pixels et reconstruction des artefacts sans modifier les métriques archivées.
- PDF C2 (5 pages), C3 (2 pages), rapport consolidé (6 pages), fiche M01 (1 page) dans deliverables/.

## À faire ensemble
- Désigner l’interlocuteur et renseigner les contributions réelles.
- Réaliser l’annotation humaine des sorties via les grilles human_review.csv.
- Relire les hypothèses pédagogiques et confirmer les modalités de remise.
- Préparer le PowerPoint et répéter la soutenance plus tard, selon la demande du groupe.

## Pour consulter
Commencer par README.md, docs/08_suivi_exigences.md, docs/17_checklist_remise.md et deliverables/Rapport_consolide_FraudLab.pdf. Les documents datés et campagnes initiales sont des archives ; les résultats courants sont ceux indiqués dans le rapport consolidé.

## Pour exécuter
Le dépôt ne contient ni données brutes, poids, base SQLite, sauvegardes ou secrets. Suivre README.md pour télécharger les entrées et reconstruire les artefacts. Le lien 127.0.0.1 est local à chaque ordinateur ; GitHub n’héberge pas l’application en fonctionnement.

## Publication terminée
Les 181 fichiers ont été publiés et vérifiés le 23 novembre 2026 sur https://github.com/tauzinflavio/GenAI-LLM. Détail et commit dans docs/27_publication_github.md.
