import os
import nbformat as nbf

def create_notebook_1():
    """Notebook 1: Collecte et Scraping."""
    nb = nbf.v4.new_notebook()
    
    # Title & Introduction
    nb.cells.append(nbf.v4.new_markdown_cell(
        "# Projet MLA : Analyse des offres d'emploi IT au Maroc\n"
        "## Notebook 1 : Collecte et Scraping des Données\n\n"
        "Ce notebook illustre la première étape du projet : la collecte de données sur les portails d'emploi marocains "
        "(`Rekrute` et `MarocAnnonces`).\n\n"
        "### Objectifs :\n"
        "1. Se connecter aux portails de recrutement et extraire les annonces d'emploi du secteur IT/Informatique au Maroc.\n"
        "2. Gérer le contournement des protections anti-scraping (User-Agents, Delays) et l'encodage.\n"
        "3. Stocker les données brutes dans des fichiers CSV structurés."
    ))
    
    # Imports & Setup
    nb.cells.append(nbf.v4.new_markdown_cell(
        "### 1. Configuration et Importations"
    ))
    nb.cells.append(nbf.v4.new_code_cell(
        "import os\n"
        "import pandas as pd\n"
        "from src.scraping.rekrute_scraper import RekruteScraper\n"
        "from src.scraping.marocannonces_scraper import MarocAnnoncesScraper\n"
        "from src.scraping.scraper_manager import main as run_scraper_manager\n\n"
        "print(\"Environnement configuré avec succès !\")"
    ))

    # Details about blocked sites
    nb.cells.append(nbf.v4.new_markdown_cell(
        "### 2. Analyse des Portails et Stratégie de Scraping\n"
        "- **Rekrute** : Les offres d'emploi IT sont regroupées sous la catégorie Informatique (`s=3`). "
        "Les détails des offres sont extraits à partir d'éléments `<li>` non nommés en classifiant leur texte.\n"
        "- **MarocAnnonces** : Les offres d'emploi sont filtrées sur le domaine informatique. Les détails sont structurés sous forme de paires clé/valeur dans des listes.\n"
        "- **Emploi.ma / Bayt.ma** : Bloquent activement les requêtes automatisées standard (retournent un code statut `403 Forbidden`). "
        "Par souci de stabilité, nous concentrons notre collecte sur les deux premières plateformes viables."
    ))

    # Running Scrapers
    nb.cells.append(nbf.v4.new_markdown_cell(
        "### 3. Exécution de la Collecte et Sauvegarde\n"
        "Nous lançons l'orchestrateur de scraping `scraper_manager.py` pour collecter les offres."
    ))
    nb.cells.append(nbf.v4.new_code_cell(
        "# Exécution de l'orchestrateur avec 8 pages par site\n"
        "df_raw = run_scraper_manager(use_cache=True, max_pages_rekrute=8, max_pages_ma=8)\n"
        "print(f\"Données collectées : {df_raw.shape[0]} lignes, {df_raw.shape[1]} colonnes.\")"
    ))

    # Inspection
    nb.cells.append(nbf.v4.new_markdown_cell(
        "### 4. Aperçu des données brutes récoltées"
    ))
    nb.cells.append(nbf.v4.new_code_cell(
        "if not df_raw.empty:\n"
        "    display(df_raw.head(3))\n"
        "    print(df_raw['source'].value_counts())\n"
        "else:\n"
        "    print(\"Aucune donnée récoltée. Vérifiez que la collecte s'est bien déroulée.\")"
    ))

    # Save notebook
    os.makedirs("notebooks", exist_ok=True)
    with open("notebooks/1_collecte_scraping.ipynb", "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print("Notebook 1 created.")


def create_notebook_2():
    """Notebook 2: Nettoyage et EDA."""
    nb = nbf.v4.new_notebook()
    
    # Title & Intro
    nb.cells.append(nbf.v4.new_markdown_cell(
        "# Projet MLA : Analyse des offres d'emploi IT au Maroc\n"
        "## Notebook 2 : Nettoyage, Traitement NLP et Analyse Exploratoire des Données (EDA)\n\n"
        "Ce notebook présente la phase de préparation des données et d'analyse exploratoire.\n\n"
        "### Objectifs :\n"
        "1. Nettoyer les textes (suppression HTML, caractères spéciaux, tokenisation, stop words, lemmatisation en français/anglais).\n"
        "2. Labelliser objectivement la variable cible `Niveau_du_poste` (Junior, Confirmé, Senior).\n"
        "3. Extraire les technologies requises (langages, frameworks, outils) et générer des features numériques.\n"
        "4. Visualiser les distributions et les tendances clés du marché IT marocain."
    ))

    # Imports & Setup
    nb.cells.append(nbf.v4.new_markdown_cell(
        "### 1. Importation des librairies et chargement des données"
    ))
    nb.cells.append(nbf.v4.new_code_cell(
        "import os\n"
        "import pandas as pd\n"
        "import numpy as np\n"
        "import matplotlib.pyplot as plt\n"
        "import seaborn as sns\n"
        "from src.preprocessing.clean_data import DataCleaner\n\n"
        "sns.set_theme(style=\"whitegrid\")\n"
        "df_raw_path = \"data/raw/jobs_raw_latest.csv\"\n"
        "if os.path.exists(df_raw_path):\n"
        "    df_raw = pd.read_csv(df_raw_path)\n"
        "    print(f\"Données brutes chargées : {len(df_raw)} lignes\")\n"
        "else:\n"
        "    print(\"Fichier de données brutes introuvable. Exécutez d'abord le scraping.\")"
    ))

    # Preprocessing execution
    nb.cells.append(nbf.v4.new_markdown_cell(
        "### 2. Nettoyage et Traitement NLP\n"
        "Nous appliquons la classe `DataCleaner` pour filtrer les doublons, éliminer le bruit textuel, lemmatiser les mots, "
        "et générer le niveau de poste cible (`Niveau_du_poste`)."
    ))
    nb.cells.append(nbf.v4.new_code_cell(
        "cleaner = DataCleaner()\n"
        "df_cleaned = cleaner.process()\n"
        "if df_cleaned is not None:\n"
        "    display(df_cleaned[['titre_poste', 'Niveau_du_poste', 'nombre_technologies']].head(5))"
    ))

    # Exploratory Data Analysis
    nb.cells.append(nbf.v4.new_markdown_cell(
        "### 3. Visualisations et Statistiques Descriptives\n"
        "Analysons maintenant les distributions des postes, des villes, et des technologies les plus demandées au Maroc."
    ))

    # Plot 1: Target distribution
    nb.cells.append(nbf.v4.new_markdown_cell(
        "#### A. Distribution de la variable cible `Niveau_du_poste`"
    ))
    nb.cells.append(nbf.v4.new_code_cell(
        "plt.figure(figsize=(7, 4))\n"
        "sns.countplot(data=df_cleaned, x='Niveau_du_poste', palette='viridis', order=['Junior', 'Confirmé', 'Senior'])\n"
        "plt.title(\"Distribution du Niveau des Postes IT au Maroc\")\n"
        "plt.xlabel(\"Niveau\")\n"
        "plt.ylabel(\"Nombre d'offres\")\n"
        "plt.show()"
    ))

    # Plot 2: Top cities
    nb.cells.append(nbf.v4.new_markdown_cell(
        "#### B. Répartition géographique des offres (Top Villes)"
    ))
    nb.cells.append(nbf.v4.new_code_cell(
        "top_villes = df_cleaned['ville'].value_counts().head(10)\n"
        "plt.figure(figsize=(10, 5))\n"
        "sns.barplot(x=top_villes.values, y=top_villes.index, palette='mako')\n"
        "plt.title(\"Top 10 des Villes avec le plus d'Offres d'Emploi IT\")\n"
        "plt.xlabel(\"Nombre d'offres\")\n"
        "plt.ylabel(\"Ville\")\n"
        "plt.show()"
    ))

    # Plot 3: Top technologies
    nb.cells.append(nbf.v4.new_markdown_cell(
        "#### C. Technologies les plus demandées"
    ))
    nb.cells.append(nbf.v4.new_code_cell(
        "tech_cols = [col for col in df_cleaned.columns if col.startswith('tech_')]\n"
        "tech_counts = df_cleaned[tech_cols].sum().sort_values(ascending=False).head(15)\n"
        "tech_names = [c.replace('tech_', '').upper() for c in tech_counts.index]\n\n"
        "plt.figure(figsize=(10, 5))\n"
        "sns.barplot(x=tech_counts.values, y=tech_names, palette='rocket')\n"
        "plt.title(\"Top 15 des Technologies les Plus Demandées\")\n"
        "plt.xlabel(\"Nombre d'offres\")\n"
        "plt.ylabel(\"Technologie\")\n"
        "plt.show()"
    ))

    # Plot 4: Contract types
    nb.cells.append(nbf.v4.new_markdown_cell(
        "#### D. Types de Contrats Proposés"
    ))
    nb.cells.append(nbf.v4.new_code_cell(
        "contrats = df_cleaned['type_contrat'].value_counts().head(5)\n"
        "plt.figure(figsize=(6, 6))\n"
        "plt.pie(contrats.values, labels=contrats.index, autopct='%1.1f%%', colors=sns.color_palette('pastel'), startangle=140)\n"
        "plt.title(\"Répartition des Types de Contrats\")\n"
        "plt.show()"
    ))

    # Save notebook
    with open("notebooks/2_nettoyage_eda.ipynb", "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print("Notebook 2 created.")


def create_notebook_3():
    """Notebook 3: Machine Learning & Clustering."""
    nb = nbf.v4.new_notebook()
    
    # Title & Intro
    nb.cells.append(nbf.v4.new_markdown_cell(
        "# Projet MLA : Analyse des offres d'emploi IT au Maroc\n"
        "## Notebook 3 : Machine Learning pour la Classification et le Clustering\n\n"
        "Ce notebook présente la modélisation prédictive supervisée et non supervisée.\n\n"
        "### Objectifs :\n"
        "1. Diviser les données en ensembles d'entraînement et de test.\n"
        "2. Construire un pipeline scikit-learn combinant vectorisation TF-IDF textuelle et standardisation numérique.\n"
        "3. Entraîner et optimiser les hyperparamètres de modèles (Régression Logistique, Random Forest, SVM).\n"
        "4. Analyser les métriques de classification (Classification Report, Matrice de Confusion).\n"
        "5. Appliquer l'algorithme K-Means pour segmenter les offres et profiler les métiers de l'IT."
    ))

    # Imports & Setup
    nb.cells.append(nbf.v4.new_markdown_cell(
        "### 1. Chargement des données prétraitées"
    ))
    nb.cells.append(nbf.v4.new_code_cell(
        "import pandas as pd\n"
        "import numpy as np\n"
        "from src.models.train import ModelTrainer\n\n"
        "trainer = ModelTrainer()\n"
        "df = trainer.load_data()\n"
        "print(f\"Données nettoyées chargées : {df.shape[0]} lignes.\")\n"
        "display(df['Niveau_du_poste'].value_counts())"
    ))

    # Classification Models
    nb.cells.append(nbf.v4.new_markdown_cell(
        "### 2. Entraînement et Évaluation des Modèles de Classification\n"
        "Nous lançons l'entraînement supervisé qui compare la Régression Logistique, le Random Forest et le SVM, "
        "avec recherche d'hyperparamètres par validation croisée (`GridSearchCV`). Le meilleur modèle est sauvegardé."
    ))
    nb.cells.append(nbf.v4.new_code_cell(
        "best_pipeline = trainer.train_classification(df)"
    ))

    # Clustering Models
    nb.cells.append(nbf.v4.new_markdown_cell(
        "### 3. Clustering non supervisé des offres d'emploi avec K-Means\n"
        "Nous appliquons K-Means pour regrouper les offres d'emploi selon leurs descriptions (TF-IDF) et caractéristiques numériques. "
        "Le nombre optimal de clusters est choisi automatiquement via l'analyse du score de silhouette."
    ))
    nb.cells.append(nbf.v4.new_code_cell(
        "trainer.run_clustering(df)"
    ))

    # Save notebook
    with open("notebooks/3_machine_learning_clustering.ipynb", "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print("Notebook 3 created.")


def create_notebook_4():
    """Notebook 4: Inférence."""
    nb = nbf.v4.new_notebook()
    
    # Title & Intro
    nb.cells.append(nbf.v4.new_markdown_cell(
        "# Projet MLA : Analyse des offres d'emploi IT au Maroc\n"
        "## Notebook 4 : Pipeline d'Inférence\n\n"
        "Ce notebook montre comment utiliser le modèle entraîné pour prédire le niveau requis (Junior, Confirmé, Senior) "
        "d'une nouvelle offre d'emploi IT à partir de son titre et de sa description."
    ))

    # Imports & Setup
    nb.cells.append(nbf.v4.new_markdown_cell(
        "### 1. Chargement du prédicteur"
    ))
    nb.cells.append(nbf.v4.new_code_cell(
        "import os\n"
        "import sys\n"
        "from src.models.predict import JobLevelPredictor\n\n"
        "try:\n"
        "    predictor = JobLevelPredictor()\n"
        "    print(\"Modèle de prédiction chargé avec succès !\")\n"
        "except Exception as e:\n"
        "    print(f\"Erreur de chargement (le modèle doit être d'abord entraîné via train.py ou le Notebook 3) : {e}\")"
    ))

    # Single Prediction Example
    nb.cells.append(nbf.v4.new_markdown_cell(
        "### 2. Test d'inférence interactif\n"
        "Définissez un titre de poste et une description pour évaluer le niveau prédit."
    ))
    nb.cells.append(nbf.v4.new_code_cell(
        "test_title = \"Développeur Fullstack React / Node.js Senior\"\n"
        "test_desc = \"\"\"\n"
        "Nous recherchons un expert Fullstack pour piloter l'architecture de nos projets.\n"
        "Vous possédez au moins 6 ans d'expérience sur React, Node.js et AWS.\n"
        "Capacité à encadrer une équipe technique (lead dev), concevoir des solutions robustes et animer les rituels agiles.\n"
        "\"\"\"\n\n"
        "res = predictor.predict(test_title, test_desc)\n"
        "print(f\"Niveau prédit : {res['predicted_level']}\")\n"
        "if res['probabilities']:\n"
        "    print(\"Probabilités :\")\n"
        "    for label, prob in res['probabilities'].items():\n"
        "        print(f\"  - {label} : {prob*100:.2f}%\")"
    ))

    # Real-world Cases Test
    nb.cells.append(nbf.v4.new_markdown_cell(
        "### 3. Exemples comparatifs"
    ))
    nb.cells.append(nbf.v4.new_code_cell(
        "exemples = [\n"
        "    {\n"
        "        \"title\": \"Ingénieur DevOps Débutant\",\n"
        "        \"desc\": \"Rattaché à l'équipe Infra, vous intervenez sur Docker, Kubernetes et Git. Jeune diplômé accepté avec stage de fin d'études significatif.\"\n"
        "    },\n"
        "    {\n"
        "        \"title\": \"Lead QA Testeur\",\n"
        "        \"desc\": \"Nous cherchons un profil confirmé (4 ans d'expérience) pour rédiger les plans de test, implémenter Selenium et assurer la qualité logicielle.\"\n"
        "    }\n"
        "]\n\n"
        "for idx, ex in enumerate(exemples):\n"
        "    r = predictor.predict(ex['title'], ex['desc'])\n"
        "    print(f\"Exemple {idx+1} : {ex['title']}\")\n"
        "    print(f\"  Prediction : {r['predicted_level']}\")\n"
        "    if r['probabilities']:\n"
        "        probs_str = \", \".join([f\"{k}: {v*100:.1f}%\" for k, v in r['probabilities'].items()])\n"
        "        print(f\"  Confidence : {probs_str}\")\n"
        "    print()"
    ))

    # Save notebook
    with open("notebooks/4_inference.ipynb", "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print("Notebook 4 created.")


if __name__ == "__main__":
    create_notebook_1()
    create_notebook_2()
    create_notebook_3()
    create_notebook_4()
