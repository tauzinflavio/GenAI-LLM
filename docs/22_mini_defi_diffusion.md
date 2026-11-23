# Mini-défi — lecture papier et code officiel
Équipe Ahmed, Meriem, Flavio. Analyse documentaire du 23 novembre 2026 ; responsable à désigner.

Article : Kotelnikov et al., TabDDPM, ICML 2023, https://proceedings.mlr.press/v202/kotelnikov23a.html.
Dépôt officiel étudié : yandex-research/tab-ddpm, commit **b476257dd460b778ba09eb97f7a51d6490fa17f8**. Licence MIT. Les trois fichiers consultés et leurs empreintes sont dans data/scientific_code_manifest.json. Il s’agit d’une lecture du code, pas d’une exécution ni d’une reproduction des résultats du dépôt officiel.

## Équation et hypothèses
Pour les variables numériques, x_t = sqrt(alpha_bar_t) x_0 + sqrt(1-alpha_bar_t) epsilon, avec epsilon gaussien standard et alpha_bar produit des (1-beta_s). Cela suppose un bruit gaussien isotrope et une représentation numérique adaptée. La perte MSE cible le bruit. Le traitement des catégories utilise un autre processus et n’est pas reproduit par notre DDPM bancaire.

## Tenseur et code
Dans notre application, x_0 et epsilon ont la forme [batch, 29], t la forme [batch]. Les coefficients temporels sont étendus en [batch, 1]. Le réseau renvoie [batch, 29]. Dans le dépôt officiel, [gaussian_q_sample, lignes 172–181](https://github.com/yandex-research/tab-ddpm/blob/b476257dd460b778ba09eb97f7a51d6490fa17f8/tab_ddpm/gaussian_multinomial_diffsuion.py#L172) effectue le bruitage. mixed_loss à partir de la ligne 591 sépare les champs numériques et catégoriels et appelle cette fonction.

## Configuration à changer et expérience proposée
Dans [exp/churn2/ddpm_cb_best/config.toml](https://github.com/yandex-research/tab-ddpm/blob/b476257dd460b778ba09eb97f7a51d6490fa17f8/exp/churn2/ddpm_cb_best/config.toml#L24), la ligne 24 définit num_timesteps = 100. Comparer prospectivement 100 et 200 pas nécessiterait de réentraîner les modèles concernés et de comparer utilité et temps à budget déclaré. Cette ablation du dépôt officiel n’a pas été exécutée. Le projet a déjà testé deux ratios d’augmentation x1/x4 et trois seeds ; ce sont ses configurations réellement évaluées.

## Métrique, coût et limite
Métrique principale bancaire : AP du détecteur sur transactions réelles indépendantes. Le coût de notre expérience est documenté par les durées d’entraînement/génération, 100 évaluations réseau par échantillon et les artefacts V1. Coût complet en euros et énergie réelle : ND. Le dépôt officiel dépend d’un ancien environnement Python 3.9 / Torch 1.10 CUDA ; notre environnement est distinct. La lecture de sa fonction ne suffit pas à annoncer la reproduction de TabDDPM.
