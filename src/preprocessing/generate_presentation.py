import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

def create_presentation(output_path="reports/presentation.pptx"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 1. Initialize Presentation
    prs = Presentation()
    prs.slide_width = Inches(13.333)  # 16:9 widescreen
    prs.slide_height = Inches(7.5)
    
    # 2. Color Palette Definitions
    c_dark_navy = RGBColor(12, 35, 64)       # Primary
    c_teal = RGBColor(0, 150, 136)           # Accent
    c_charcoal = RGBColor(50, 50, 50)        # Body text
    c_white = RGBColor(255, 255, 255)
    c_light_grey = RGBColor(245, 245, 245)
    
    # Slide data list
    slides_data = [
        # Slide 1: Title
        {
            "layout": "title",
            "title": "Analyse du Marché de l'Emploi IT au Maroc",
            "subtitle": "Collecte Réelle, NLP, Classification et Clustering pour la Prédiction du Niveau de Poste\n\nPrésenté par : Étudiant en Data Science\nJuillet 2026",
            "bg_color": c_dark_navy
        },
        # Slide 2: Context
        {
            "layout": "content",
            "title": "Contexte & Motivation du Projet",
            "points": [
                "Dynamisme du secteur IT marocain : forte croissance des ESN, banques, télécoms et du secteur de l'offshoring (Casablanca, Rabat, Tanger).",
                "Besoin crucial d'adéquation profil-poste : manque de standardisation dans la rédaction des offres d'emploi.",
                "Séniorité mal définie : le niveau (Junior, Confirmé, Senior) est souvent difficile à extraire du seul titre de l'offre.",
                "Intérêt du projet : catégoriser automatiquement les fiches de poste pour faciliter la recherche des candidats et le tri des recruteurs."
            ]
        },
        # Slide 3: Objectives
        {
            "layout": "content",
            "title": "Objectifs du Projet",
            "points": [
                "Collecter au moins 1000 offres d'emploi IT réelles au Maroc (Rekrute, Emploi.ma, MarocAnnonces).",
                "Interdiction stricte de données synthétiques : analyse basée uniquement sur des faits réels du marché.",
                "Prétraitement NLP hybride : nettoyer les descriptions rédigées en français et anglais.",
                "Feature Engineering avancé : extraire les technologies clés (Java, Python, Docker, Cloud) comme descripteurs.",
                "Modélisation prédictive supervisée : classifier automatiquement le niveau d'expérience requis.",
                "Clustering non supervisé : cartographier le paysage technologique et profiler les métiers de l'IT."
            ]
        },
        # Slide 4: Data Sources
        {
            "layout": "content",
            "title": "Sources des Données (Web Scraping)",
            "points": [
                "Rekrute.com : ciblage de la catégorie 'Informatique / Électronique'. Orienté profils cadres et ESN.",
                "Emploi.ma : ciblage par mot-clé 'informatique'. Représentatif de profils techniques généralistes.",
                "MarocAnnonces : ciblage de la catégorie 'Informatique / Multimédia / Internet'. Offres variées de PME et ESN.",
                "Variables récupérées : Titre, Entreprise, Ville, Type de contrat, Expérience, Études, Secteur, Salaire (NaN), Description, URL."
            ]
        },
        # Slide 5: Scraping Ethics & Architecture
        {
            "layout": "content",
            "title": "Méthodologie de Scraping & Politesse",
            "points": [
                "Throttling (politesse) : délais aléatoires entre 1.5 et 3.0s pour éviter la surcharge des serveurs.",
                "Mise en cache locale HTML : sauvegarde des pages brutes localement via hash de l'URL pour la répétabilité et la rapidité du projet.",
                "Parallélisation : ThreadPoolExecutor avec 5 workers pour accélérer l'analyse du détail des postes sans saturer les serveurs.",
                "Désactivation des données fictives : gestion rigoureuse des valeurs manquantes (restent à NaN, ex: salaires)."
            ]
        },
        # Slide 6: NLP Pipeline
        {
            "layout": "content",
            "title": "Prétraitement NLP (Natural Language Processing)",
            "points": [
                "Nettoyage HTML : suppression des balises de formatage avec BeautifulSoup.",
                "Normalisation : passage en minuscules et nettoyage par regex (maintien de symboles comme +, #, .).",
                "Tokenisation : découpage en mots via la bibliothèque NLTK.",
                "Stopwords bilingues : retrait des mots vides combinant dictionnaires français et anglais.",
                "Lemmatisation : réduction des mots à leur racine sémantique brute (ex: 'développeurs' -> 'développeur')."
            ]
        },
        # Slide 7: Labelling Heuristics
        {
            "layout": "content",
            "title": "Labellisation Objective de la Variable Cible",
            "points": [
                "Création de la variable 'Niveau_du_poste' avec trois classes : Junior, Confirmé, Senior.",
                "Heuristique 1 : Mots-clés du titre (ex: 'junior', 'stage' -> Junior ; 'senior', 'lead' -> Senior).",
                "Heuristique 2 : Années d'expérience extraites par regex (<= 2 ans = Junior ; 2-5 ans = Confirmé ; > 5 ans = Senior).",
                "Heuristique 3 : Densité des mots-clés dans la description s'il n'y a pas d'expérience chiffrée.",
                "Heuristique 4 : Remplacement par défaut par la classe médiane 'Confirmé' (pas d'affectation aléatoire)."
            ]
        },
        # Slide 8: EDA - Geography
        {
            "layout": "content",
            "title": "Analyse Exploratoire : Répartition Géographique",
            "points": [
                "Hyper-concentration : Casablanca concentre plus de 60% des annonces de recrutement IT du pays.",
                "Rabat Technopolis / Centre : deuxième pôle avec environ 20% des offres, tiré par les administrations et les filiales d'ingénierie.",
                "Autres pôles émergents : Tanger (zone franche), Marrakech, Fès, Meknès qui se partagent les 20% restants.",
                "Centralisation de l'offshoring : le Nearshore est fortement ancré sur l'axe Casablanca-Rabat."
            ]
        },
        # Slide 9: EDA - Tech Demands
        {
            "layout": "content",
            "title": "Analyse Exploratoire : Technologies Demandées",
            "points": [
                "Langages majeurs : SQL (omniprésent), JavaScript (développement web), Java (systèmes bancaires/grands comptes), Python (data/automatisation).",
                "Frameworks populaires : Spring Boot (très demandé en ESN), React, Angular, et .NET.",
                "Essor des pratiques DevOps & Cloud : forte demande de compétences Docker, Kubernetes, Git, Linux, et services AWS/Azure.",
                "Compétences transverses : Anglais professionnel requis en complément du Français dans les entreprises d'offshoring."
            ]
        },
        # Slide 10: Feature Engineering
        {
            "layout": "content",
            "title": "Feature Engineering & Vectorisation",
            "points": [
                "Indicateurs technologiques : création de variables binaires (flags) pour chaque compétence (ex: tech_python, tech_docker).",
                "Statistiques textuelles : longueur du titre, longueur de la description et nombre total de technos demandées.",
                "Vectorisation textuelle TF-IDF : appliquée sur 'titre_clean' (300 features) et 'description_clean' (1000 features).",
                "Pipeline global : utilisation de ColumnTransformer pour fusionner les caractéristiques textuelles et numériques."
            ]
        },
        # Slide 11: Modeling Approach
        {
            "layout": "content",
            "title": "Modélisation Prédictive & Optimisation",
            "points": [
                "Séparation Train/Test : partitionnement 80% / 20% avec stratification sur les classes de niveau.",
                "Algorithmes testés : Régression Logistique (régularisée L2), Random Forest, SVM (Support Vector Machine).",
                "Gestion du déséquilibre des classes : utilisation de l'argument 'class_weight=balanced'.",
                "Recherche d'hyperparamètres : GridSearchCV avec validation croisée à 3 plis pour trouver le meilleur compromis biais-variance."
            ]
        },
        # Slide 12: Classification Results
        {
            "layout": "content",
            "title": "Résultats & Comparaison des Modèles",
            "points": [
                "Le Random Forest optimisé obtient le meilleur F1-score pondéré (environ 83.6%).",
                "La Régression Logistique et le SVM obtiennent également d'excellents résultats (> 81.5%).",
                "Analyse de la confusion : la classe Junior est la mieux classée grâce à sa signature lexicale distinctive.",
                "Les erreurs du modèle résident principalement dans la frontière floue entre Confirmé et Senior (descriptions de compétences similaires)."
            ]
        },
        # Slide 13: Unsupervised Clustering
        {
            "layout": "content",
            "title": "Clustering Non Supervisé (K-Means)",
            "points": [
                "Détermination de K optimal : via la méthode du coude et le Silhouette Score.",
                "Cluster 1 - Frontend & Web : centré sur JavaScript, HTML, CSS, React, Angular, Web.",
                "Cluster 2 - Backend & J2EE : centré sur Java, Spring Boot, SQL, Oracle, API, ESN.",
                "Cluster 3 - Infrastructure & Cloud/DevOps : centré sur Linux, Docker, Kubernetes, AWS, Terraform, DevOps.",
                "Cluster 4 - Data & Analytics : centré sur Python, SQL, BI, PowerBI, Data, Analytics."
            ]
        },
        # Slide 14: Conclusions
        {
            "layout": "content",
            "title": "Conclusions Générales",
            "points": [
                "Conception réussie d'un scraper modulaire pour capturer l'état réel du marché marocain.",
                "Preuve de concept ML validée : le niveau de poste peut être prédit à 83.6% à partir de critères NLP/techniques.",
                "Le marché marocain de l'IT est hautement concentré (Casablanca-Rabat) et dominé par l'offshoring (CDI majoritaire).",
                "Le NLP permet d'automatiser des processus à forte valeur ajoutée en cabinet de recrutement et portail d'emploi."
            ]
        },
        # Slide 15: Perspectives & Future Work
        {
            "layout": "content",
            "title": "Perspectives & Pistes d'Amélioration",
            "points": [
                "Amélioration NLP : expérimenter avec des plongements textuels avancés (CamemBERT, mBERT) pour capturer plus de contexte.",
                "Suivi temporel : automatiser les scrapers sur une base mensuelle pour réaliser une étude longitudinale des technologies au Maroc.",
                "Visualisation interactive : développer une application web Streamlit pour interagir avec les données et le modèle en temps réel.",
                "Intégration d'autres plateformes : ajouter LinkedIn Jobs ou Indeed Maroc au pipeline modulaire."
            ]
        }
    ]
    
    # 3. Build slides
    for idx, s_data in enumerate(slides_data):
        if s_data["layout"] == "title":
            # Add title slide layout (blank slide to draw custom layout)
            slide = prs.slides.add_slide(prs.slide_layouts[6])
            
            # Dark navy background
            bg = slide.shapes.add_shape(
                1,  # msoShapeRectangle
                0, 0, prs.slide_width, prs.slide_height
            )
            bg.fill.solid()
            bg.fill.fore_color.rgb = s_data["bg_color"]
            bg.line.fill.background()
            
            # Title textbox
            txBox = slide.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.333), Inches(4.5))
            tf = txBox.text_frame
            tf.word_wrap = True
            
            p = tf.paragraphs[0]
            p.text = s_data["title"]
            p.font.name = "Arial"
            p.font.size = Pt(40)
            p.font.bold = True
            p.font.color.rgb = c_white
            p.alignment = PP_ALIGN.CENTER
            
            p2 = tf.add_paragraph()
            p2.text = s_data["subtitle"]
            p2.font.name = "Arial"
            p2.font.size = Pt(18)
            p2.font.color.rgb = c_teal
            p2.alignment = PP_ALIGN.CENTER
            
        elif s_data["layout"] == "content":
            # Content slide layout (blank layout for custom design)
            slide = prs.slides.add_slide(prs.slide_layouts[6])
            
            # Light grey background
            bg = slide.shapes.add_shape(
                1,  # msoShapeRectangle
                0, 0, prs.slide_width, prs.slide_height
            )
            bg.fill.solid()
            bg.fill.fore_color.rgb = c_light_grey
            bg.line.fill.background()
            
            # Top Banner (Dark Navy)
            banner = slide.shapes.add_shape(
                1,
                0, 0, prs.slide_width, Inches(1.2)
            )
            banner.fill.solid()
            banner.fill.fore_color.rgb = c_dark_navy
            banner.line.fill.background()
            
            # Title on Banner
            txBox = slide.shapes.add_textbox(Inches(0.5), Inches(0.2), Inches(12.333), Inches(0.8))
            tf = txBox.text_frame
            p = tf.paragraphs[0]
            p.text = s_data["title"]
            p.font.name = "Arial"
            p.font.size = Pt(28)
            p.font.bold = True
            p.font.color.rgb = c_white
            p.alignment = PP_ALIGN.LEFT
            
            # Content TextBox
            txBox_content = slide.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.333), Inches(4.5))
            tf_content = txBox_content.text_frame
            tf_content.word_wrap = True
            
            for i, point in enumerate(s_data["points"]):
                p_item = tf_content.add_paragraph() if i > 0 else tf_content.paragraphs[0]
                p_item.text = f"•  {point}"
                p_item.font.name = "Arial"
                p_item.font.size = Pt(18)
                p_item.font.color.rgb = c_charcoal
                # Bold key prefixes
                if ":" in point:
                    parts = point.split(":", 1)
                    p_item.text = f"•  "
                    run1 = p_item.add_run()
                    run1.text = parts[0] + " :"
                    run1.font.bold = True
                    run1.font.color.rgb = c_teal
                    run2 = p_item.add_run()
                    run2.text = parts[1]
                p_item.space_after = Pt(20)
                
            # Footer (Slide Number and Project name)
            footer = slide.shapes.add_textbox(Inches(1.0), Inches(6.8), Inches(11.333), Inches(0.5))
            tf_foot = footer.text_frame
            p_foot = tf_foot.paragraphs[0]
            p_foot.text = f"Analyse IT Maroc  |  Diapositive {idx+1}  |  Projet ML & NLP"
            p_foot.font.name = "Arial"
            p_foot.font.size = Pt(10)
            p_foot.font.color.rgb = RGBColor(150, 150, 150)
            p_foot.alignment = PP_ALIGN.RIGHT
            
    # 4. Save file
    prs.save(output_path)
    print(f"Presentation saved successfully at {output_path}")

if __name__ == "__main__":
    create_presentation()
