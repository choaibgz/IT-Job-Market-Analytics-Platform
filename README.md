# Analyse des offres d'emploi IT au Maroc et prédiction du niveau de poste

Ce projet universitaire de Data Science et de Data Engineering a pour mission d'analyser le marché de l'emploi informatique au Maroc et de prédire le niveau des postes (`Junior`, `Confirmé`, `Senior`) à partir de données réelles collectées sur des portails d'emploi marocains.

## Table des matières
1. [Objectifs du Projet](#objectifs-du-projet)
2. [Architecture du Projet](#architecture-du-projet)
3. [Installation et Configuration](#installation-et-configuration)
4. [Étapes du Projet](#étapes-du-projet)
   - [Collecte des données (Scraping)](#collecte-des-données-scraping)
   - [Nettoyage & Traitement NLP](#nettoyage--traitement-nlp)
   - [Analyse Exploratoire (EDA)](#analyse-exploratoire-eda)
   - [Machine Learning & Modélisation](#machine-learning--modélisation)
   - [Clustering (K-Means)](#clustering-k-means)
5. [Inférence & Prédiction](#inférence--prédiction)
6. [Livrables Finaux](#livrables-finaux)

---

## Objectifs du Projet
- **Collecte Réelle** : Récupérer des offres d'emploi IT réelles au Maroc à partir de **Rekrute**, **Emploi.ma** et **MarocAnnonces**.
- **NLP & Feature Engineering** : Nettoyer les descriptions textuelles (suppression de balises, minuscules, tokenisation, stopwords, lemmatisation) et extraire des variables clés (langages, frameworks, outils cloud/devops).
- **Classification Supervisée** : Entraîner et comparer des modèles de classification pour prédire le niveau de poste (`Junior`, `Confirmé`, `Senior`).
- **Clustering Non Supervisé** : Identifier les principaux domaines de l'IT marocain grâce à K-Means.
- **Zéro donnée fictive** : Le projet repose intégralement sur des offres réelles d'emploi au Maroc.

---

## Architecture du Projet
├── data/
│   ├── raw/                  # Données brutes de scraping (jobs_raw_latest.csv)
│   ├── processed/            # Données nettoyées (cleaned_jobs.csv)
│   └── cache/                # Cache local pour éviter les requêtes répétitives
├── src/
│   ├── scraping/             # Modules de scraping par plateforme
│   │   ├── rekrute_scraper.py
│   │   ├── marocannonces_scraper.py
│   │   └── scraper_manager.py
│   ├── preprocessing/        # Scripts de nettoyage et de NLP
│   │   └── clean_data.py
│   └── models/               # Entraînement et prédiction
│       ├── train.py
│       └── predict.py
├── notebooks/                # Notebooks Jupyter interactifs
│   ├── 1_collecte_scraping.ipynb
│   ├── 2_nettoyage_eda.ipynb
│   ├── 3_machine_learning_clustering.ipynb
│   └── 4_inference.ipynb
├── reports/                  # Documents finaux
│   ├── figures/              # Graphiques générés
│   └── scientific_report.md  # Rapport académique de ~30 pages
├── models_saved/             # Fichier du modèle sérialisé (.pkl)
│   └── job_level_model.pkl
├── generate_notebooks.py     # Générateur programmatique des 4 notebooks
├── requirements.txt          # Dépendances Python du projet
└── README.md                 # Documentation globale
```

---

## Installation et Configuration

### Prérequis
- Python 3.10 ou supérieur
- Accès Internet pour la collecte des données

### Installation
1. Clonez ou ouvrez le projet dans votre workspace :
   ```bash
   cd c:/dev/NewMLAProject
   ```
2. Créez un environnement virtuel Python et activez-le :
   ```bash
   python -m venv .venv
   # Sur Windows :
   .venv\Scripts\activate
   ```
3. Installez les packages requis :
   ```bash
   pip install -r requirements.txt
   ```

---

## Étapes du Projet

### Collecte des données (Scraping)
Pour exécuter le scraping et collecter les offres d'emploi IT réelles (avec mise en cache automatique dans `data/cache` pour éviter les requêtes HTTP répétitives) :
```bash
python -m src.scraping.scraper_manager
```

### Nettoyage & Traitement NLP
Pour éliminer les doublons, nettoyer les descriptions et structurer les variables (y compris la variable cible `Niveau_du_poste`) :
```bash
python -m src.preprocessing.clean_data
```

### Machine Learning & Modélisation
Pour entraîner le classifieur, exécuter l'optimisation des hyperparamètres par GridSearchCV, comparer les modèles, générer les courbes et matrices de confusion, et faire le clustering K-Means :
```bash
python -m src.models.train
```

---

## Inférence & Prédiction
Une fois le modèle entraîné, vous pouvez prédire le niveau d'une nouvelle offre d'emploi en important la classe `JobLevelPredictor` dans `src/models/predict.py` :
```python
from src.models.predict import JobLevelPredictor

predictor = JobLevelPredictor()
res = predictor.predict(
    title="Développeur Python Data Analyst",
    description="Nous recherchons un ingénieur de données avec 4 ans d'expérience en Python, SQL, et Pandas..."
)
print(res)
# Résultat : {'predicted_level': 'Confirmé', 'probabilities': {'Junior': 0.12, 'Confirmé': 0.78, 'Senior': 0.10}}
```

## Livrables Finaux
- **4 Notebooks Jupyter** : Collecte, EDA, ML/Clustering, Inférence
- **Rapport Scientifique** : `reports/scientific_report.md` (~30 pages)
- **Modèle entraîné** : `models_saved/job_level_model.pkl`
- **Figures** : `reports/figures/` (matrices de confusion, courbes de clustering)

---

## Auteurs & Licence
Projet académique réalisé sous licence MIT.
