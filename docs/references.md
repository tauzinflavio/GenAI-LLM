# Pistes scientifiques initiales
Sources pédagogiques : pack projet ECE du 3 novembre 2026 et fiches C3 fournies. Les suggestions du chat partagé restent soumises aux consignes du cours.

## DDPM
Ho, Jain et Abbeel, Denoising Diffusion Probabilistic Models, 2020, arXiv:2006.11239v2.
https://arxiv.org/abs/2006.11239v2
Notice et résumé consultés. Apport pour le projet : fondements du bruitage/débruitage probabiliste. Les résultats annoncés en images ne démontrent aucun gain sur notre tâche tabulaire.

## TabDDPM
Kotelnikov, Baranchuk, Rubachev et Babenko, TabDDPM: Modelling Tabular Data with Diffusion Models, ICML 2023, arXiv:2209.15421v2 (7 octobre 2024).
https://arxiv.org/abs/2209.15421v2
Notice et résumé consultés. Apport : diffusion de variables tabulaires hétérogènes continues et discrètes. Les comparaisons annoncées avec GAN/VAE sur des benchmarks restent à examiner avant transfert à la fraude.

Les analyses DDPM/TabDDPM sont dans docs/13_analyse_scientifique.md ; le code officiel est étudié au commit figé dans docs/22_mini_defi_diffusion.md. Les mentions « notice consultée » ci-dessus décrivent l’étape initiale, pas le statut actuel.

## Analyse réalisée
Voir docs/13_analyse_scientifique.md pour les sections méthodologiques et expérimentales examinées, leurs limites et la correspondance avec notre code. Les notices ci-dessus conservent l’état de lecture initial.
