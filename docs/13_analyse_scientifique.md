# Analyse scientifique et correspondance avec l’implémentation

## Ho, Jain et Abbeel — DDPM, 2020
Référence examinée, arXiv:2006.11239v2. Sections fondements, processus inverse et objectif simplifié.

L’objectif est de générer des images par inversion d’un bruitage gaussien. Les variables principales sont l’observation x₀, son état bruité xₜ, le temps t et le bruit ε. Le réseau prédit ε à partir de xₜ et t. L’objectif simplifié minimise une erreur quadratique. Le processus inverse utilise cette prédiction pour calculer une moyenne gaussienne et échantillonner l’état précédent.

Le protocole porte notamment sur CIFAR-10 et LSUN, avec comparaison de qualité d’image et ablations de paramétrisation. Les auteurs annoncent sur CIFAR-10 un FID de 3,17 et un Inception Score de 9,46. Ces métriques d’image n’établissent aucune utilité en fraude bancaire.

Pour notre projet, le transfert pertinent est la prédiction du bruit et le sampling inverse. Le choix d’un MLP tabulaire, de 100 pas et du prétraitement bancaire doit être évalué dans notre protocole. Les résultats du papier ne valident pas ces adaptations. [Article et équations](https://arxiv.org/html/2006.11239v2)

## Kotelnikov et al. — TabDDPM, ICML 2023
Référence examinée, PMLR 202, pages 17564–17579. Sections méthode, protocole et comparaison qualitative.

TabDDPM combine diffusion gaussienne pour les variables numériques et multinomiale pour les catégories. Il utilise une transformation quantile, un MLP et un conditionnement de classe. La perte associe MSE et termes KL catégoriels.

L’évaluation couvre quinze jeux tabulaires. Les références incluent des générateurs GAN/VAE et une interpolation de type SMOTE. L’utilité est évaluée en entraînant des prédicteurs sur des données synthétiques, puis en testant sur des observations réelles. Les hyperparamètres sont sélectionnés sur validation. Les résultats rapportés favorisent fréquemment TabDDPM, tandis que les méthodes simples restent compétitives.

Notre implémentation est un DDPM gaussien sur une seule classe, avec standardisation et log-montant. Elle ne reproduit pas les transformations, pertes mixtes, conditionnement et recherche d’hyperparamètres de TabDDPM. Cette différence limite la comparaison. La proximité aux données train est un contrôle complémentaire, sans garantie générale de confidentialité. [Article, sections 4 et 5, tableaux 1 et 2](https://proceedings.mlr.press/v202/kotelnikov23a/kotelnikov23a.pdf)

## Correspondance mathématiques–code propre à FraudLab
Notre code définit alpha[t] = 1 − beta[t] et cumulative[t] comme le produit des alpha jusqu’au pas t inclus. Son indice zéro représente le premier pas bruité ; il ne désigne pas l’observation propre.

Le bruitage implémenté est

x_bruité = sqrt(cumulative[t]) × x_propre + sqrt(1 − cumulative[t]) × bruit.

La cible du réseau est le bruit tiré, et l’erreur est la moyenne du carré de l’écart entre bruit prédit et bruit tiré. Les trois composantes temporelles concaténées sont t normalisé, sin(πt) et cos(πt). Le réseau possède deux couches cachées de 128 unités avec SiLU.

Lors de la génération, le programme part d’un vecteur gaussien de dimension 29, parcourt les 100 indices en ordre inverse et utilise la variance postérieure calculée. Au dernier retour vers la donnée, aucun bruit supplémentaire n’est ajouté. Le réseau et la normalisation du générateur sont appris sur le sous-ensemble interne d’apprentissage des fraudes.

Le générateur produit log1p(Amount), ensuite transformé en montant dans l’application. Une valeur logarithmique négative ou hors borne conduit à un rejet explicite. Les métriques d’utilité évaluent les détecteurs sur les transactions réelles indépendantes.

## Critique de nos résultats
L’échantillon de fraudes d’apprentissage est réduit. La MSE de bruit peut diminuer sans gain utile du détecteur. Les montants rejetés montrent une limite du support appris. L’augmentation améliore certaines références descriptivement, mais son avantage sur la référence pondérée n’est pas établi par l’intervalle d’incertitude du test figé.

La comparaison de prompts révèle aussi une interaction entre modèle et instruction. Le prompt V2 améliore B seul sur le jeu séparé et dégrade A+B. Cette observation soutient le maintien d’une référence simple et d’un contrôle indépendant du modèle.

## Code officiel et réutilisation
Le dépôt des auteurs de TabDDPM est identifié comme implémentation officielle et affiche une licence MIT. FraudLab conserve sa propre implémentation pédagogique. Une future reprise du code officiel devra figer le commit et conserver les mentions de licence applicables. [Dépôt officiel](https://github.com/yandex-research/tab-ddpm)
