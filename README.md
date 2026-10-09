# TP M2-1 — Signal PPG — Équipe 02

Travail réalisé à partir du notebook étudiant de Nicolas Laurio, Digi5, module 2, Epitech MBA Santé, IA & IoT (9 octobre 2026).

## Livrables demandés

- [Notebook principal exécuté](analyses/m2_tp1/TP_M2_1_Signal_PPG_eq02.ipynb) : **43 cellules d'origine**, questions 1 à 9 complétées, sorties visibles.
- [Synthèse](analyses/m2_tp1/synthese.md) : les cinq lignes demandées, la ligne de résultats et le tableau générés par le code fourni.
- [Les six bonus](analyses/m2_tp1/bonus/TP_M2_1_Bonus_eq02.ipynb) : notebook exécuté dans un dossier séparé. Les tableaux détaillés sont dans `bonus/resultats/`.

Dans le code du notebook principal, seuls `EQUIPE = "2"` et le texte de `SYNTHESE` ont été remplis. Aucun calcul ni code d'export fourni n'a été changé. Les essais demandés ont été réalisés, leurs résultats sont consignés dans les réponses, puis les réglages de référence ont été rétablis.

La mise à jour du professeur (`TP_M2_1_Signal_PPG 1.ipynb`) est intégrée : elle contrôle et convertit le numéro d'équipe, accepte par exemple `"02"`, vérifie la plage 1–99 et normalise le choix des données synthétiques. Elle ne modifie pas les algorithmes du TP. Une réexécution confirme que les sorties numériques du groupe 2 sont inchangées.

## Données et résultats du groupe 2

Le groupe 2 analyse **BIDMC 02** : 60 001 mesures à 125 Hz sur 480 secondes et 481 valeurs du moniteur à 1 Hz. Les CSV locaux ont été vérifiés à l'aide du manifeste SHA-256 officiel de PhysioNet.

- FC moyenne estimée : **90,89 bpm**, référence : **91,07 bpm**.
- MAE : **0,799 bpm avec filtre**, **0,775 bpm sans filtre**. Le filtre n'améliore donc pas la MAE sur cet enregistrement.
- Mouvement simulé de gain 3 : **19,08 bpm** de MAE pendant l'artefact, pire écart **44,14 bpm**.
- Avec la règle qualité à 0,15 : **0,80 bpm** de MAE sur les valeurs transmises, **90,1 %** de transmission ; aucune FC transmise pendant l'artefact.

## Exécution locale

Python 3.10 ou plus récent et un accès Internet pour récupérer les données absentes :

```powershell
python -m pip install -r requirements.txt
python executer_tp.py
```

Le script lance le notebook depuis la racine du dépôt, sans modifier ses cellules. Cela conserve le chemin d'export `analyses/m2_tp1/synthese.md` prévu dans le sujet. Le notebook principal télécharge automatiquement les deux CSV du groupe 2 dans `data/` s'ils sont absents. Il affiche explicitement un avertissement s'il utilise le repli synthétique ; les résultats livrés ici proviennent bien de BIDMC.

Pour consulter les graphiques dans Jupyter :

```powershell
python -m notebook
```

Dans Google Colab, importer le notebook principal, puis exécuter les cellules dans l'ordre. Ne pas oublier de télécharger le notebook exécuté et `synthese.md` avant de fermer la session.

## Bonus séparés

```powershell
python executer_tp.py --bonus
```

1. Comparaison avec `PULSE`, puis comparaison des deux estimations à `HR`.
2. Estimation spectrale par FFT, fenêtre de Hann de 8 s, bande 0,7–3 Hz.
3. Filtrage causal `sosfilt` et mesure du décalage des pics.
4. Corrélation avec la forme moyenne des battements et limites d'un ajout par condition ET.
5. Mouvement réel sur **PPG-DaLiA S1** : PPG à 64 Hz, accélération à 32 Hz et référence ECG alignée sur des fenêtres 8 s / 2 s. Ce sujet est distinct du patient BIDMC 02. Il s'agit d'une démonstration sur un sujet, pas d'une évaluation des 15 sujets.
6. Analyse des **53 enregistrements BIDMC**, distribution des erreurs et inspection des cas difficiles.

Le téléchargement initial des bonus est volumineux : les 106 CSV BIDMC et la lecture d'environ 1,3 Go de l'archive UCI pour extraire S1. Les données déjà présentes sont réutilisées. Aucun repli synthétique n'est permis pour la comparaison des 53 patients. Le test synthétique du bonus 4 est identifié comme tel.

## Sources et attribution

- Pimentel et al., *BIDMC PPG and Respiration Dataset*, v1.0.0, [PhysioNet](https://physionet.org/content/bidmc/1.0.0/), DOI [10.13026/C2208R](https://doi.org/10.13026/C2208R), licence ODC-BY 1.0.
- Pimentel et al., *Toward a Robust Estimation of Respiratory Rate From Pulse Oximeters*, IEEE TBME 64(8), 2017, DOI 10.1109/TBME.2016.2613124 ; Goldberger et al., *PhysioBank, PhysioToolkit, and PhysioNet*, Circulation, 2000.
- Reiss, Indlekofer et Schmidt (2019), [PPG-DaLiA, UCI](https://archive.ics.uci.edu/dataset/495/ppg+dalia), DOI [10.24432/C53890](https://doi.org/10.24432/C53890), licence CC BY 4.0 ; Reiss et al., *Deep PPG*, Sensors 19(14), 2019.

Les données brutes sont exclues de Git conformément au TP. Usage pédagogique : ces expériences ne constituent pas une validation médicale.
