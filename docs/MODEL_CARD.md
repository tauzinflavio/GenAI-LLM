# Fiche système / modèle — FraudLab
Version du 23 novembre 2026. Équipe : Ahmed, Meriem, Flavio. Interlocuteur, contributions et propriétaire d’exploitation : **à décider**, confirmation du groupe. Dépôt : https://github.com/tauzinflavio/GenAI-LLM.

## Usage et personnes concernées
POC pédagogique local de détection supervisée et d’assistance factuelle à la revue d’alertes. Utilisateur cible : analyste ; aucun client réel identifié, aucun compte manipulable. Usage exclu : décider une fraude certaine, bloquer un compte, effectuer un virement ou déployer en production bancaire.

## Composants et versions
- Détecteur : régression logistique pondérée, seed 42, paramètres dans `configs/experiment_v1.json`. Score **non calibré**, seuil F1 de validation.
- Générateur : DDPM gaussien inconditionnel, classe fraude seule, 29 entrées, MLP 128–128, 100 pas, 2 000 updates, deux ratios x1/x4, trois seeds. Adaptation propre, pas reproduction de TabDDPM.
- A : HuggingFaceTB/SmolLM2-360M-Instruct, révision a10cc1512eabd3dde888204e902eca88bddb4951.
- B : Qwen/Qwen2.5-0.5B-Instruct, révision 7ae557604adf67be50417f59c2c2f167def9a775.
- Licences modèles déclarées Apache-2.0 ; liens et révisions dans `configs/llm_models.json`. Inférence CPU locale, décodage glouton, 100 tokens max. Prompt `configs/prompts/report_v2.txt`. Scripts et dépendances versionnés.

## Données et populations
OpenML1597 v1 : 284807 transactions et 492 fraudes brutes ; après dédoublonnage 283726 et 473. Partitions temporelles 170235/56745/56746, avec 342/57/74 fraudes. V1–V28 anonymisées/PCA ; Amount d’unité non confirmée. Période courte, origine historique, absence de contexte client ou d’attributs protégés exploitables. Licence source « Public » : aucun droit détaillé de redistribution présumé. Données/poids/SQLite exclus du dépôt.
LLM : fixtures entièrement fictives, jamais le label réel d’une transaction. TP04 : 10 cas construits ; M01 : 12 tâches distinctes. Les cas ont été gelés avant leurs campagnes respectives ; TP04 reste construit après les explorations V1/V2.

## Évaluation et décisions
Détecteur retenu avant test : AP final 0,7442. DDPM x4 : 0,7551 ; delta 0,0110, IC bootstrap95 [−0,0601 ; 0,0843]. Pas de supériorité démontrée.
TP04 : A5/10, B9/10, routing7/10, cascade9/10. Trois gardes communes incluses ; pour les seuls cas LLM, B et cascade6/7. B7 appels, cascade12 ; p95 1,866s contre4,120s sur dix cas. Ce n’est ni une validation humaine ni une expertise bancaire. Cas montant nul non résolu.
M01 : 3/12 pour chacun selon grille automatique stricte/lexicale, pas jugement sémantique. Aucun retenu selon seuil figé. Relecture humaine en attente ; aucun annotateur fictif.

## Ressources et coût
Mac Apple M2/8Go, CPU. Appels et tokens mesurés. Coût API0 EUR, coût complet réel ND ; calculs financiers hypothétiques séparés. Énergie électrique réelle ND ; scénarios W×durée/PUE/facteur carbone documentés, pas empreinte réelle.

## Garde-fous et risques reliés aux tests
| Risque | Contrôle | Preuve |
|---|---|---|
| Fuite entre splits | dédoublonnage, groupes temporels, transformations train | experiments/data_audit.json |
| Copie / mémorisation | proximité, unicité, limites explicites | generation_quality.csv, sans garantie de confidentialité |
| Hallucination / format | contrat exact, abstention visible, revue humaine requise | TP04 traces et human_review.csv |
| Injection / source absente / conflit | notes non fiables, gardes déterministes de fixtures | T07–T10 ; ne prouve pas détection documentaire générale |
| Action bancaire non autorisée | aucune API d’action bancaire, schémas fermés | tests/check_api.py |
| Panne / dépassement | budget tokens/appels, délais, admission1, reprise explicite | tp04_robustness.json ; evidence/incident.json |
| Logs / rétention | pas de prompt dans journal service, rétention30jours | service_safety.json |
| Biais et couverture | tests par catégorie et limites PCA | TP04 by_category.csv ; aucune équité démographique démontrée |

## Exploitation et escalade
Écoute127.0.0.1 uniquement ; accès analyste simulé. Pas de TLS/SSO/IAM/HA de production. En panne : arrêter/reprendre selon runbook ; aucun fallback cloud. Opérateur de séance : personne qui lance l’application, désignation nominative à décider. Pas d’alerte externe automatique ; dashboard signale disponibilité et limites. Retour au rapport déterministe si le LLM échoue.
GO démonstration locale supervisée, NO-GO production bancaire. Ne pas prétendre une conformité RGPD/AI Act certifiée.

## Reproductibilité et évolution
README, requirements, snapshots protocole/code et manifestes. Les corrections UI ne changent pas les résultats archivés. Les hypothèses chiffrées prospectives dans `configs/confirmation_future.json` concernent de nouveaux tests ; aucune date de gel rétroactive ni nouveau réglage sur l’ancien test.
