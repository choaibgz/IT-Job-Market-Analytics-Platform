import os
import joblib
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix, silhouette_score
from sklearn.cluster import KMeans
from nltk.corpus import stopwords

class ModelTrainer:
    def __init__(self, data_path="data/processed/cleaned_jobs.csv", model_dir="models_saved", fig_dir="reports/figures"):
        self.data_path = data_path
        self.model_dir = model_dir
        self.fig_dir = fig_dir
        os.makedirs(self.model_dir, exist_ok=True)
        os.makedirs(self.fig_dir, exist_ok=True)
        
    def load_data(self):
        """Load the preprocessed dataset."""
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Cleaned dataset not found at {self.data_path}. Please run cleaner first.")
        df = pd.read_csv(self.data_path)
        # Drop rows where target or features are completely null
        df = df.dropna(subset=['Niveau_du_poste', 'description_clean', 'titre_clean'])
        return df

    def train_classification(self, df):
        """Train and evaluate multiple text+tabular classification models."""
        print("\n=== Starting Machine Learning Classification ===")
        
        # 1. Separate features and target
        X = df[['titre_clean', 'description_clean', 'nombre_technologies', 'longueur_description', 'longueur_titre'] + 
               [col for col in df.columns if col.startswith('tech_')]]
        y = df['Niveau_du_poste']
        
        # Split into train/test sets (80/20)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        print(f"Train set size: {X_train.shape[0]} samples")
        print(f"Test set size: {X_test.shape[0]} samples")
        
        # 2. Define features for ColumnTransformer
        text_features_title = 'titre_clean'
        text_features_desc = 'description_clean'
        num_features = ['nombre_technologies', 'longueur_description', 'longueur_titre']
        binary_features = [col for col in df.columns if col.startswith('tech_')]
        
        # 3. Create preprocessing pipelines
        preprocessor = ColumnTransformer(
            transformers=[
                ('txt_title', TfidfVectorizer(max_features=300, ngram_range=(1, 2)), text_features_title),
                ('txt_desc', TfidfVectorizer(max_features=1000, ngram_range=(1, 2)), text_features_desc),
                ('num', StandardScaler(), num_features),
                ('bin', 'passthrough', binary_features)
            ]
        )
        
        # 4. Define candidate models
        models = {
            'Logistic Regression': Pipeline([
                ('preprocessor', preprocessor),
                ('classifier', LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42))
            ]),
            'Random Forest': Pipeline([
                ('preprocessor', preprocessor),
                ('classifier', RandomForestClassifier(class_weight='balanced', random_state=42))
            ]),
            'SVM': Pipeline([
                ('preprocessor', preprocessor),
                ('classifier', SVC(class_weight='balanced', probability=True, random_state=42))
            ])
        }
        
        # 5. Model training and evaluation
        results = {}
        best_model_name = None
        best_f1 = 0
        best_pipeline = None
        
        for name, pipeline in models.items():
            print(f"\nTraining {name}...")
            # Hyperparameter tuning using GridSearchCV for demonstration
            if name == 'Random Forest':
                param_grid = {
                    'classifier__n_estimators': [100, 200],
                    'classifier__max_depth': [10, 20, None],
                }
                grid = GridSearchCV(pipeline, param_grid, cv=3, scoring='f1_weighted', n_jobs=1)
                grid.fit(X_train, y_train)
                pipeline = grid.best_estimator_
                print(f"Best params for Random Forest: {grid.best_params_}")
            elif name == 'Logistic Regression':
                param_grid = {
                    'classifier__C': [0.1, 1.0, 10.0]
                }
                grid = GridSearchCV(pipeline, param_grid, cv=3, scoring='f1_weighted', n_jobs=1)
                grid.fit(X_train, y_train)
                pipeline = grid.best_estimator_
                print(f"Best params for Logistic Regression: {grid.best_params_}")
            else:
                pipeline.fit(X_train, y_train)
                
            # Evaluation on test set
            y_pred = pipeline.predict(X_test)
            acc = accuracy_score(y_test, y_pred)
            report = classification_report(y_test, y_pred, output_dict=True)
            weighted_f1 = report['weighted avg']['f1-score']
            
            print(f"{name} Accuracy: {acc:.4f} | Weighted F1: {weighted_f1:.4f}")
            print(classification_report(y_test, y_pred))
            
            # Keep track of best model
            if weighted_f1 > best_f1:
                best_f1 = weighted_f1
                best_model_name = name
                best_pipeline = pipeline
                
            # Plot Confusion Matrix
            cm = confusion_matrix(y_test, y_pred)
            plt.figure(figsize=(6, 5))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                        xticklabels=np.unique(y), yticklabels=np.unique(y))
            plt.title(f'Matrice de Confusion - {name}')
            plt.ylabel('Vrai niveau')
            plt.xlabel('Niveau prédit')
            plt.tight_layout()
            
            fig_path = os.path.join(self.fig_dir, f"confusion_matrix_{name.lower().replace(' ', '_')}.png")
            plt.savefig(fig_path)
            plt.close()
            
        print(f"\nBest Model: {best_model_name} with Weighted F1: {best_f1:.4f}")
        
        # Save the best pipeline
        model_path = os.path.join(self.model_dir, "job_level_model.pkl")
        joblib.dump(best_pipeline, model_path)
        print(f"Saved the best pipeline to {model_path}")
        
        return best_pipeline

    def run_clustering(self, df):
        """Cluster jobs using K-Means and analyze profiles."""
        print("\n=== Starting K-Means Clustering ===")
        
        # 1. Transform texts using TF-IDF for clustering
        french_stop = list(stopwords.words('french'))
        tfidf = TfidfVectorizer(max_features=500, stop_words=french_stop)
        text_matrix = tfidf.fit_transform(df['description_clean'].fillna(''))
        
        # Convert to dense matrix and add numeric features
        scaler = StandardScaler()
        num_scaled = scaler.fit_transform(df[['nombre_technologies', 'longueur_description']])
        
        # Combine features
        features = np.hstack((text_matrix.toarray(), num_scaled))
        
        # 2. Elbow method and Silhouette Score to find optimal K
        K_range = range(2, 8)
        inertias = []
        silhouettes = []
        
        for k in K_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(features)
            inertias.append(kmeans.inertia_)
            silhouettes.append(silhouette_score(features, kmeans.labels_))
            
        # Plot Elbow Method
        plt.figure(figsize=(10, 4))
        plt.subplot(1, 2, 1)
        plt.plot(K_range, inertias, 'bo-')
        plt.xlabel('Nombre de clusters (K)')
        plt.ylabel('Inertie')
        plt.title('Méthode du Coude')
        
        # Plot Silhouette Scores
        plt.subplot(1, 2, 2)
        plt.plot(K_range, silhouettes, 'ro-')
        plt.xlabel('Nombre de clusters (K)')
        plt.ylabel('Silhouette Score')
        plt.title('Silhouette Score par K')
        
        plt.tight_layout()
        elbow_path = os.path.join(self.fig_dir, "clustering_elbow_silhouette.png")
        plt.savefig(elbow_path)
        plt.close()
        print(f"Clustering evaluation plots saved to {elbow_path}")
        
        # Select best K based on silhouette score
        best_k = K_range[np.argmax(silhouettes)]
        print(f"Optimal K selected: {best_k}")
        
        # Train final K-Means
        kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
        df['Cluster'] = kmeans.fit(features)
        df['Cluster'] = kmeans.labels_
        
        # Analyze cluster profiles
        print("\nCluster Profiles (Top words and tech counts):")
        # Get terms
        terms = tfidf.get_feature_names_out()
        centroids = kmeans.cluster_centers_[:, :len(terms)]
        
        for c in range(best_k):
            print(f"\nCluster {c}:")
            # Top words in cluster
            top_words_idx = centroids[c].argsort()[-10:][::-1]
            top_words = [terms[idx] for idx in top_words_idx]
            print(f"  Top mots: {', '.join(top_words)}")
            
            # Mean tech count and description length
            cluster_jobs = df[df['Cluster'] == c]
            mean_tech = cluster_jobs['nombre_technologies'].mean()
            mean_len = cluster_jobs['longueur_description'].mean()
            print(f"  Taille du cluster: {len(cluster_jobs)} offres")
            print(f"  Nombre moyen de technos: {mean_tech:.2f}")
            print(f"  Longueur moyenne description: {mean_len:.2f}")
            
            # Identify domain based on top words/techs
            tech_cols = [col for col in df.columns if col.startswith('tech_')]
            if len(cluster_jobs) > 0:
                top_techs = cluster_jobs[tech_cols].mean().sort_values(ascending=False).head(5)
                top_tech_list = [t.replace('tech_', '') for t in top_techs.index if top_techs[t] > 0.1]
                print(f"  Technologies fréquentes: {', '.join(top_tech_list)}")
                
        # Save updated data with clusters
        df.to_csv(self.data_path, index=False, encoding='utf-8')
        print(f"Preprocessed dataset updated with 'Cluster' column.")

    def run(self):
        df = self.load_data()
        self.train_classification(df)
        self.run_clustering(df)

if __name__ == "__main__":
    trainer = ModelTrainer()
    trainer.run()
