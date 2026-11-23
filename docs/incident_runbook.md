# TP08 — runbook local
## Prérequis et lancement
Python 3.14, environnement installé depuis requirements.txt, artefacts préparés avec python src/prepare_demo.py. Aucun secret API requis. Depuis la racine : FRAUDLAB_SERVING=1 python -m uvicorn app:app --app-dir src --host 127.0.0.1 --port 8782. Attendre la fin du chargement et du warm-up. Consulter /healthz puis /readyz. Versions des modèles dans configs/llm_models.json.

## Vérifications
python scripts/service_checks.py smoke --base-url http://127.0.0.1:8782 ; python scripts/service_checks.py load --base-url http://127.0.0.1:8782 --concurrency 1 --requests 12, puis palier 3 / 18 requêtes. Les preuves de charge existantes sont protégées contre l’écrasement. Pour une répétition, archiver la campagne ou utiliser une copie neuve du projet.

## Panne observée
Cause confirmée : arrêt volontaire SIGTERM du processus writer de la seule instance jetable lancée par scripts/incident_test.py. healthz reste 200, readyz et generate passent à 503. Aucun transfert vers un cloud. Le script vérifie l’identité PID de son propre serveur avant d’agir. Les tests sur un autre système ne sont pas autorisés par ce script.

Commande reproductible : python scripts/incident_test.py. Au premier essai, la vérification de parenté via inventaire système a été interdite par l’environnement et l’expérience s’est arrêtée avant injection. La version corrigée vérifie l’identité de sa propre instance sans inventaire global ; l’expérience complète a ensuite été exécutée. Cette limite n’est pas masquée.

Action : arrêter proprement l’instance affectée, relancer la même commande et les mêmes modèles, attendre /readyz, puis exécuter un smoke réel. Reprise observée 18.61 s après l’injection, warm-up et inférence compris. Un seul incident ne démontre pas une disponibilité générale.

## Diagnostic et alerte
- health 200 / ready 503 : API vivante, un backend n’est pas prêt. Vérifier erreurs de chargement, poids présents et état des workers ; garder le service indisponible.
- HTTP 429 : admission occupée, attendre la fin ; aucun retry en boucle.
- HTTP 504 : limite d’inférence atteinte ; worker interrompu. Relancer le service après diagnostic, réduire contexte ou charge dans une nouvelle configuration identifiée.
- HTTP 502 : sortie modèle invalide ou backend en erreur ; conserver statut d’échec et revue humaine.
- Base SQLite inaccessible : suspendre les écritures, conserver une copie et diagnostiquer le stockage. Ne pas écraser la base saine.

En démonstration, l’opérateur qui lance le service suit ces signaux. Responsable permanent et canal d’alerte humain à désigner par Ahmed, Meriem et Flavio. Aucun envoi de message automatique n’a été configuré.

## Sauvegarde et restauration
python scripts/backup_db.py --check crée data/backups/activity.sqlite et une copie de restauration neuve, puis compare nombre d’événements et PRAGMA integrity_check. Ne jamais publier ces fichiers. Une destination déjà présente est refusée ; utiliser un nouveau nom pour un nouveau contrôle. Restaurer une vraie base nécessite arrêter le service, sauvegarder l’existante et vérifier la copie hors ligne avant remplacement. Le test réalisé n’a écrasé aucune base.

## Rollback et risques résiduels
Garder la version précédente de code/configs et les empreintes de modèles. Tant que Git n’est pas importé, l’archive de partage et son manifeste fournissent une trace de contenu, pas un historique de commits. Revenir au rapport déterministe si la génération n’est pas disponible. Une version précédente ne doit pas exposer le service au réseau. POC sans haute disponibilité, sans SSO/TLS de production et sans revue humaine complétée : ouverture bancaire réelle interdite dans notre décision.

## Réactivation des workers depuis l’interface
Le bouton Réactiver l’analyse locale appelle /api/recover, qui accepte 202 puis recharge seulement les workers manquants. /readyz reste 503 jusqu’à la fin du chargement et du warm-up. Aucune ancienne demande n’est rejouée. Le test scripts/check_recovery.py arrête le worker de sa propre instance sur 8785 et confirme ensuite une nouvelle inférence réelle. Délai observé : 10,38 s pour cette récupération ciblée, distinct des 18,61 s du redémarrage complet initial. Preuve evidence/recovery_endpoint.json.

Un premier test de cette nouvelle fonction avait révélé un état prêt annoncé avant la fin du chargement, suivi d’un refus 429. Il est conservé dans recovery_endpoint_initial_failure.json. La correction utilise un état de disponibilité après warm-up et un indicateur de reprise en cours. Le second test complet a réussi. Les snapshots du code TP04 sont conservés dans experiments/results/tp04/code ; la correction de readiness a été ajoutée après ce benchmark, sans changer le prompt ou les résultats archivés.
