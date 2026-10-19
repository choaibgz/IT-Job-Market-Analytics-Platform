import os
import nbformat as nbf

def create_collection_notebook(output_dir):
    nb = nbf.v4.new_notebook()
    
    nb['cells'] = [
        nbf.v4.new_markdown_cell(
            "# Étape 1 : Collecte et Scraping de données réelles\n"
            "Ce notebook montre comment les scrapers pour Rekrute, Emploi.ma, et MarocAnnonces "
            "ont été développés et comment les données ont été collectées de manière modulaire et stockées."
        ),
        nbf.v4.new_code_cell(
            "import os\n"
            "import pandas as pd\n"
            "from src.scraping.scraper_manager import ScraperManager\n\n"
            "# 1. Initialiser le gestionnaire de scrapers\n"
            "manager = ScraperManager()\n"
            "print('Gestionnaire initialisé avec succès !')"
        ),
        nbf.v4.new_markdown_cell(
            "## Exécution du Scraping\n"
            "Nous allons lancer la collecte pour extraire les offres d'emploi IT marocaines. "
            "Les requêtes sont parallélisées et utilisent un système de mise en cache locale "
            "dans `data/cache` afin d'éviter la surcharge des serveurs cibles."
        ),
        nbf.v4.new_code_cell(
            "# Pour la démonstration, nous collectons les données sur 3 pages par site\n"
            "df_raw = manager.run_all(max_pages=3)\n"
            "print(f'Taille du dataset collecté : {len(df_raw)} lignes')"
        ),
        nbf.v4.new_markdown_cell(
            "## Aperçu des données collectées\n"
            "Regardons les colonnes disponibles et les premières lignes de notre dataset brut."
        ),
        nbf.v4.new_code_cell(
            "if not df_raw.empty:\n"
            "    display(df_raw.head(3))\n"
            "    display(df_raw.info())\n"
            "else:\n"
            "    print('Aucune donnée collectée. Veuillez vérifier les scrapers.')"
        )
    ]
    
    path = os.path.join(output_dir, "01_data_collection.ipynb")
    with open(path, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
    print(f"Created {path}")

def create_eda_notebook(output_dir):
    nb = nbf.v4.new_notebook()
    
    nb['cells'] = [
        nbf.v4.new_markdown_cell(
            "# Étape 2 : Nettoyage de données (NLP) et Analyse Exploratoire (EDA)\n"
            "Dans ce notebook, nous nettoyons les textes (descriptions et titres), "
            "déduisons de manière objective le niveau de poste cible, et effectuons "
            "une analyse statistique approfondie du marché de l'IT marocain."
        ),
        nbf.v4.new_code_cell(
            "import os\n"
            "import pandas as pd\n"
            "import numpy as np\n"
            "import matplotlib.pyplot as plt\n"
            "import seaborn as sns\n"
            "from wordcloud import WordCloud\n"
            "from src.preprocessing.clean_data import DataCleaner\n\n"
            "sns.set_theme(style='darkgrid')\n"
            "print('Bibliothèques importées !')"
        ),
        nbf.v4.new_markdown_cell(
            "## Exécution du nettoyage et du Feature Engineering\n"
            "Le script `clean_data.py` nettoie les descriptions textuelles (NLP), extrait "
            "les compétences techniques sous forme de variables binaires (flags) et crée "
            "la variable cible `Niveau_du_poste` (Junior, Confirmé, Senior)."
        ),
        nbf.v4.new_code_cell(
            "cleaner = DataCleaner()\n"
            "df_cleaned = cleaner.process()\n"
            "if df_cleaned is not None:\n"
            "    print(f'Dataset nettoyé prêt ! Taille : {len(df_cleaned)} lignes')"
        ),
        nbf.v4.new_markdown_cell(
            "## Analyse Exploratoire des Données (EDA)\n\n"
            "### 1. Distribution de la variable cible `Niveau_du_poste`"
        ),
        nbf.v4.new_code_cell(
            "plt.figure(figsize=(7, 5))\n"
            "sns.countplot(data=df_cleaned, x='Niveau_du_poste', palette='viridis', order=['Junior', 'Confirmé', 'Senior'])\n"
            "plt.title('Distribution des niveaux de postes IT au Maroc')\n"
            "plt.xlabel('Niveau du poste')\n"
            "plt.ylabel(\"Nombre d'offres\")\n"
            "plt.show()"
        ),
        nbf.v4.new_markdown_cell(
            "### 2. Répartition géographique des offres IT au Maroc\n"
            "Quelle ville recrute le plus dans le secteur informatique ?"
        ),
        nbf.v4.new_code_cell(
            "top_villes = df_cleaned['ville'].value_counts().head(10)\n"
            "plt.figure(figsize=(10, 5))\n"
            "sns.barplot(x=top_villes.values, y=top_villes.index, palette='mako')\n"
            "plt.title(\"Top 10 des villes qui recrutent dans l'IT au Maroc\")\n"
            "plt.xlabel(\"Nombre d'offres\")\n"
            "plt.ylabel('Ville')\n"
            "plt.show()"
        ),
        nbf.v4.new_markdown_cell(
            "### 3. Top des technologies et compétences demandées\n"
            "Analysons la fréquence des langages, frameworks et outils DevOps/Cloud."
        ),
        nbf.v4.new_code_cell(
            "tech_cols = [col for col in df_cleaned.columns if col.startswith('tech_')]\n"
            "tech_frequencies = df_cleaned[tech_cols].mean().sort_values(ascending=False).head(15)\n"
            "tech_names = [col.replace('tech_', '').upper() for col in tech_frequencies.index]\n\n"
            "plt.figure(figsize=(12, 6))\n"
            "sns.barplot(x=tech_frequencies.values * 100, y=tech_names, palette='rocket')\n"
            "plt.title('Top 15 des compétences technologiques les plus demandées (%)')\n"
            "plt.xlabel('Pourcentage des offres (%)')\n"
            "plt.ylabel('Technologie')\n"
            "plt.show()"
        ),
        nbf.v4.new_markdown_cell(
            "### 4. Nuage de mots des descriptions d'offres"
        ),
        nbf.v4.new_code_cell(
            "text = ' '.join(df_cleaned['description_clean'].dropna())\n"
            "wc = WordCloud(width=800, height=400, background_color='white', max_words=100).generate(text)\n"
            "plt.figure(figsize=(12, 6))\n"
            "plt.imshow(wc, interpolation='bilinear')\n"
            "plt.axis('off')\n"
            "plt.title('Mots-clés les plus fréquents dans les descriptions de poste')\n"
            "plt.show()"
        )
    ]
    
    path = os.path.join(output_dir, "02_exploratory_data_analysis.ipynb")
    with open(path, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
    print(f"Created {path}")

def create_modeling_notebook(output_dir):
    nb = nbf.v4.new_notebook()
    
    nb['cells'] = [
        nbf.v4.new_markdown_cell(
            "# Étape 3 : Modélisation (Machine Learning) et Clustering\n"
            "Ce notebook présente la modélisation prédictive avec plusieurs algorithmes supervisés "
            "et l'analyse non supervisée des profils de postes par K-Means."
        ),
        nbf.v4.new_code_cell(
            "import pandas as pd\n"
            "import numpy as np\n"
            "import matplotlib.pyplot as plt\n"
            "from src.models.train import ModelTrainer\n\n"
            "trainer = ModelTrainer()\n"
            "print('Trainer prêt !')"
        ),
        nbf.v4.new_markdown_cell(
            "## Exécution du pipeline d'entraînement\n"
            "Nous allons lancer l'entraînement pour comparer la Régression Logistique, "
            "le Random Forest, et le Support Vector Machine (SVM). Le meilleur modèle "
            "sera automatiquement sauvegardé sous `models_saved/job_level_model.pkl`."
        ),
        nbf.v4.new_code_cell(
            "df = trainer.load_data()\n"
            "best_pipeline = trainer.train_classification(df)"
        ),
        nbf.v4.new_markdown_cell(
            "## Clustering non supervisé avec K-Means\n"
            "Nous regroupons les offres d'emploi pour profiler les différents types de postes "
            "(Développement Web, Data, DevOps/Cloud, etc.)."
        ),
        nbf.v4.new_code_cell(
            "trainer.run_clustering(df)"
        ),
        nbf.v4.new_markdown_cell(
            "## Visualisation des performances\n"
            "Visualisons les graphiques de performances générés dans `reports/figures/`."
        ),
        nbf.v4.new_code_cell(
            "from IPython.display import Image, display\n"
            "import glob\n\n"
            "figures = glob.glob('reports/figures/*.png')\n"
            "for fig in figures:\n"
            "    print(f'Figure : {fig}')\n"
            "    display(Image(filename=fig))"
        )
    ]
    
    path = os.path.join(output_dir, "03_model_training_evaluation.ipynb")
    with open(path, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
    print(f"Created {path}")

def create_inference_notebook(output_dir):
    nb = nbf.v4.new_notebook()
    
    nb['cells'] = [
        nbf.v4.new_markdown_cell(
            "# Étape 4 : Inférence et Prédiction\n"
            "Ce notebook montre comment charger le modèle pré-entraîné "
            "et l'utiliser pour prédire en temps réel le niveau d'une nouvelle offre d'emploi IT."
        ),
        nbf.v4.new_code_cell(
            "import os\n"
            "from src.models.predict import JobLevelPredictor\n\n"
            "# Charger le prédicteur\n"
            "predictor = JobLevelPredictor()\n"
            "print('Modèle de prédiction chargé avec succès !')"
        ),
        nbf.v4.new_markdown_cell(
            "## Test sur une nouvelle offre d'emploi réelle (Exemple 1 : Junior)\n"
            "Nous allons passer le titre et la description d'une offre pour profil Débutant."
        ),
        nbf.v4.new_code_cell(
            "title_1 = 'Développeur ReactJS Débutant'\n"
            "desc_1 = '''\n"
            "Nous recrutons un Développeur ReactJS junior ou stagiaire pour notre équipe à Rabat. \n"
            "Vous interviendrez sur le développement de nos interfaces web.\n"
            "Compétences requises : HTML, CSS, JavaScript, React. Git et Docker sont un plus. \n"
            "Une première expérience ou un stage significatif est apprécié.\n"
            "'''\n\n"
            "res_1 = predictor.predict(title_1, desc_1)\n"
            "print(f'Niveau prédit : {res_1[\"predicted_level\"]}')\n"
            "print('Probabilités :', res_1['probabilities'])"
        ),
        nbf.v4.new_markdown_cell(
            "## Test sur une offre (Exemple 2 : Senior / Expert)\n"
            "Passons maintenant une annonce pour un poste de Lead / Architecte demandant de l'expérience."
        ),
        nbf.v4.new_code_cell(
            "title_2 = 'Architecte Solutions Cloud & DevOps Senior'\n"
            "desc_2 = '''\n"
            "En tant qu'Architecte Solutions Cloud et DevOps Senior, vous concevrez les architectures Cloud. \n"
            "Nous recherchons un profil avec plus de 8 ans d'expérience. \n"
            "Compétences techniques : AWS, Azure, Terraform, Kubernetes, Docker, CI/CD, Java.\n"
            "Vous encadrerez une équipe de développeurs confirmés.\n"
            "'''\n\n"
            "res_2 = predictor.predict(title_2, desc_2)\n"
            "print(f'Niveau prédit : {res_2[\"predicted_level\"]}')\n"
            "print('Probabilités :', res_2['probabilities'])"
        )
    ]
    
    path = os.path.join(output_dir, "04_inference.ipynb")
    with open(path, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
    print(f"Created {path}")

def generate_all():
    output_dir = "notebooks"
    os.makedirs(output_dir, exist_ok=True)
    create_collection_notebook(output_dir)
    create_eda_notebook(output_dir)
    create_modeling_notebook(output_dir)
    create_inference_notebook(output_dir)

if __name__ == "__main__":
    generate_all()
