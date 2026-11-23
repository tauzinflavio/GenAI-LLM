# Sensibilité environnementale pédagogique

Les seules mesures de départ sont les durées d’inférence de la comparaison V2 sur douze cas. La puissance et le facteur carbone ci-dessous sont des hypothèses de sensibilité, sans source empirique. Aucun pays, datacenter ou appareil réel ne leur est associé. Ce document fournit un calcul d’ordre de grandeur conditionnel, distinct d’un bilan carbone mesuré.

| Scénario hypothétique | Puissance moyenne supposée | Multiplicateur d’infrastructure | Facteur carbone supposé |
|---|---|---|---|
| Bas | 10 W | 1 | 20 gCO₂e/kWh |
| Central | 25 W | 1 | 50 gCO₂e/kWh |
| Haut | 50 W | 1 | 100 gCO₂e/kWh |

Le multiplicateur vaut 1 car le scénario représente seulement une consommation locale supposée au niveau du poste. Il n’affirme aucun PUE de datacenter. L’appellation PUE conservée dans le CSV et le calculateur est un paramètre de scénario, à justifier selon le périmètre choisi.

## Calcul central sur les durées observées

| Configuration | Cas | Énergie conditionnelle pour le lot | CO₂e conditionnel pour le lot |
|---|---|---|---|
| v1_A_mono | 12 | 0.0001227 kWh | 0.006137 g |
| v1_A_plus_B | 12 | 0.0002705 kWh | 0.013523 g |
| v2_A_mono | 12 | 0.0001641 kWh | 0.008203 g |
| v2_A_plus_B | 12 | 0.0004335 kWh | 0.021677 g |
| v2_B_mono | 12 | 0.0001212 kWh | 0.006062 g |

L’énergie est proportionnelle à la durée uniquement parce qu’une même puissance constante est supposée. Le fichier CSV fournit aussi une énergie par cas et par contrat strict réussi. Ce dernier indicateur reste un proxy formel et ne mesure pas une analyse bancaire valide.

Le chargement, les téléchargements, le train du détecteur et du DDPM, l’inactivité, la mémoire, le refroidissement non compris dans la puissance supposée et la fabrication sont exclus. La puissance réelle varie selon le modèle et la charge. Le calcul peut donc sous-estimer ou surestimer l’usage réel. Les montants très faibles concernent quelques secondes d’inférence et ce périmètre limité.

## Confirmation nécessaire
Pour une estimation défendable d’usage réel, remplacer les hypothèses par une puissance mesurée ou une source technique adaptée, un facteur carbone daté et un périmètre d’infrastructure cohérent. Refaire la comparaison avec des sorties satisfaisant un seuil de qualité fixé. Conserver les consommations d’apprentissage séparément.
