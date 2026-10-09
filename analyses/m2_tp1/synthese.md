# TP M2-1 — Synthèse de l'équipe 02

1. Source : BIDMC enregistrement 02 (PhysioNet, DOI 10.13026/C2208R, licence ODC-BY 1.0), données réelles : 60 001 échantillons à 125 Hz sur 480 s.
2. Erreur : MAE avec filtre 0,799 bpm contre 0,775 bpm sans filtre ; le filtre n'améliore pas la MAE sur ce patient au repos.
3. Artefact : gain 3 entre 200 et 240 s, MAE pendant l'artefact 19,08 bpm, pire écart 44,14 bpm ; MAE globale 2,35 bpm.
4. Règle qualité : MAE des FC transmises 0,80 bpm, transmission 90,1 % du temps et 0 % pendant l'artefact ; risque de rejeter un véritable rythme irrégulier.
5. Réglages retenus : filtre 0,5–5 Hz ordre 4, FC_MAX=180, PROEMINENCE=0,5, SEUIL_CV=0,15 ; limiter les FC erronées malgré une disponibilité réduite.

Résultats : Équipe 02 | BIDMC enregistrement 02 | FC réf. 91 bpm | MAE 0.8 bpm | MAE artefact 19.1 bpm | MAE transmise 0.8 bpm (90 % transmis) | réglage 0.5-5.0 Hz ordre 4, FC_MAX 180, seuil CV 0.15

```
                    Configuration  MAE (bpm)  MAE pendant l'artefact (bpm)  FC transmise (% du temps)
                      Sans filtre        0.8                           NaN                      100.0
                Filtre 0.5-5.0 Hz        0.8                           0.8                      100.0
           Filtre + règle qualité        0.8                           0.8                       98.3
                Filtre + artefact        2.4                          19.1                      100.0
Filtre + artefact + règle qualité        0.8                           NaN                       90.1
```
