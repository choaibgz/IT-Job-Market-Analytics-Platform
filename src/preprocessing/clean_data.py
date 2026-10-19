import os
import re
import pandas as pd
import numpy as np
import nltk
from bs4 import BeautifulSoup

# Download NLTK data required for tokenization and stopwords
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab', quiet=True)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', quiet=True)

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

class DataCleaner:
    def __init__(self):
        # Load stopwords for both French and English
        self.stop_words = set(stopwords.words('french')).union(set(stopwords.words('english')))
        self.lemmatizer = WordNetLemmatizer()
        
        # Technology keywords definitions for extraction (using raw strings to avoid syntax warnings)
        self.tech_keywords = {
            'langages': ['python', 'java', 'javascript', 'typescript', 'php', 'c#', r'c\+\+', 'c ', 'ruby', 'go', 'rust', 'kotlin', 'swift', 'scala', ' r ', 'html', 'css', 'sql'],
            'frameworks': ['react', 'angular', 'vue', 'node', 'laravel', 'django', 'flask', 'spring boot', 'symfony', r'\.net', 'flutter', 'react native', 'tensorflow', 'pytorch', 'keras', 'django', 'fastapi'],
            'databases': ['mysql', 'postgresql', 'postgres', 'oracle', 'sql server', 'mongodb', 'redis', 'cassandra', 'dynamodb', 'mariadb', 'sqlite', 'firebase'],
            'cloud': ['aws', 'amazon web services', 'azure', 'gcp', 'google cloud', 'heroku', 'openstack'],
            'devops': ['docker', 'kubernetes', 'k8s', 'git', 'gitlab', 'github', 'jenkins', 'ansible', 'terraform', 'ci/cd', 'linux', 'unix', 'devops']
        }


    def clean_html(self, text):
        """Remove HTML tags from text."""
        if not isinstance(text, str):
            return ""
        soup = BeautifulSoup(text, 'html.parser')
        return soup.get_text()

    def clean_text(self, text):
        """Standard NLP text cleaning: lowercase, remove punctuation/digits, tokenize, remove stopwords, lemmatize."""
        if not isinstance(text, str):
            return ""
        
        # Remove HTML
        text = self.clean_html(text)
        
        # Lowercase
        text = text.lower()
        
        # Remove special characters and punctuation (keep letters, spaces, and common IT chars like + and #)
        text = re.sub(r'[^a-z0-9\s\+\#\.\-]', ' ', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and short tokens, then lemmatize
        cleaned_tokens = [
            self.lemmatizer.lemmatize(token)
            for token in tokens
            if token not in self.stop_words and len(token) > 1
        ]
        
        return " ".join(cleaned_tokens)

    def extract_years_experience(self, exp_str, desc_str):
        """Extract number of years of experience from text using regex."""
        # Clean inputs
        exp_str = str(exp_str).lower() if pd.notna(exp_str) else ""
        desc_str = str(desc_str).lower() if pd.notna(desc_str) else ""
        
        # Combined text to search
        search_text = exp_str + " " + desc_str
        
        # Search patterns: "3 ans", "3ans", "3 years", "3years", "de 3 à 5 ans", "1-3 ans"
        patterns = [
            r'(\d+)\s*ans?',
            r'(\d+)\s*years?',
            r'(\d+)\s*a\s*\d+\s*ans?',
            r'(\d+)\s*-\s*\d+\s*ans?'
        ]
        
        years = []
        for pattern in patterns:
            matches = re.findall(pattern, search_text)
            for match in matches:
                try:
                    years.append(int(match))
                except ValueError:
                    pass
                    
        # Map structured strings to numbers if found in exp_str
        if not years:
            if "débutant" in exp_str or "jeune diplômé" in exp_str or "moins de 1 an" in exp_str:
                return 0
            elif "1 à 3 ans" in exp_str or "1 an" in exp_str:
                return 2
            elif "3 à 5 ans" in exp_str:
                return 4
            elif "5 à 10 ans" in exp_str or "plus de 5 ans" in exp_str:
                return 6
            elif "plus de 10 ans" in exp_str:
                return 11
                
        if years:
            # Return the median/mean of extracted years, capped realistically
            val = int(np.median(years))
            return val if val < 20 else 5
            
        return None

    def label_job_level(self, row):
        """Determine target class (Junior, Confirmé, Senior) objectively based on exp years, title, and description."""
        title = str(row['titre_poste']).lower() if pd.notna(row['titre_poste']) else ""
        exp_text = str(row['experience_demandee']).lower() if pd.notna(row['experience_demandee']) else ""
        desc = str(row['description']).lower() if pd.notna(row['description']) else ""
        
        # Step 1: Check title keywords (highest priority)
        junior_keywords = ['junior', 'stagiaire', 'stage', 'intern', 'débutant', 'jeune diplômé', 'alternance', 'graduate']
        senior_keywords = ['senior', 'lead', 'architecte', 'directeur', 'manager', 'expert', 'chef de projet', 'principal', 'head', 'vp', 'cto']
        
        # Check if title strictly matches
        for kw in junior_keywords:
            if re.search(r'\b' + kw + r'\b', title):
                return 'Junior'
        for kw in senior_keywords:
            if re.search(r'\b' + kw + r'\b', title):
                return 'Senior'
                
        # Step 2: Use years of experience if available
        years = self.extract_years_experience(row['experience_demandee'], row['description'])
        if years is not None:
            if years <= 2:
                return 'Junior'
            elif years <= 5:
                return 'Confirmé'
            else:
                return 'Senior'
                
        # Step 3: Heuristics on experience description text
        if any(kw in exp_text for kw in ['débutant', 'pas d\'expérience', '0 à 2 ans', 'moins de 1 an']):
            return 'Junior'
        if any(kw in exp_text for kw in ['5 ans', '6 ans', '7 ans', '8 ans', '10 ans', 'plus de 5', 'senior', 'expert']):
            return 'Senior'
        if any(kw in exp_text for kw in ['2 à 5 ans', '3 ans', '4 ans', 'confirmé', 'expérimenté']):
            return 'Confirmé'
            
        # Step 4: Default fallback using description keyword density
        junior_density = sum(1 for kw in junior_keywords if kw in desc)
        senior_density = sum(1 for kw in senior_keywords if kw in desc)
        
        if junior_density > senior_density:
            return 'Junior'
        elif senior_density > junior_density:
            return 'Senior'
            
        # Standard fallback for corporate posts
        return 'Confirmé'

    def extract_features(self, df):
        """Perform feature engineering by extracting tech flags, text lengths, and counts."""
        df_feats = df.copy()
        
        # Clean text columns for matching
        combined_text = (df_feats['titre_poste'].fillna('') + ' ' + df_feats['description'].fillna('')).str.lower()
        
        all_tech_cols = []
        for category, keywords in self.tech_keywords.items():
            for kw in keywords:
                # Standardize column name (e.g. spring boot -> spring_boot, .net -> net, c++ -> cpp)
                col_name = kw.replace(' ', '_').replace('+', 'p').replace('#', 'sharp').replace('.', '').strip()
                col_name = f"tech_{col_name}"
                
                # Check presence of keyword as word boundary
                pattern = r'\b' + re.escape(kw) + r'\b'
                if kw == 'c ':
                    pattern = r'\bc\b'
                elif kw == ' r ':
                    pattern = r'\br\b'
                
                df_feats[col_name] = combined_text.apply(lambda x: 1 if re.search(pattern, x) else 0)
                all_tech_cols.append(col_name)
                
        # Compute summary features
        df_feats['nombre_technologies'] = df_feats[all_tech_cols].sum(axis=1)
        df_feats['longueur_description'] = df_feats['description'].fillna('').apply(len)
        df_feats['longueur_titre'] = df_feats['titre_poste'].fillna('').apply(len)
        
        return df_feats

    def process(self, input_csv="data/raw/jobs_raw_latest.csv", output_csv="data/processed/cleaned_jobs.csv"):
        """Main processing workflow."""
        if not os.path.exists(input_csv):
            print(f"Error: {input_csv} does not exist. Run the scraper first.")
            return None

        print(f"Reading raw data from {input_csv}...")
        df = pd.read_csv(input_csv, encoding='utf-8-sig')
        print(f"Initial row count: {len(df)}")

        # 1. Drop duplicates
        df.drop_duplicates(subset=['titre_poste', 'entreprise', 'description'], inplace=True)
        df.dropna(subset=['titre_poste', 'description'], inplace=True)
        df = df[df['pays'].str.lower().str.contains('maroc', na=True)].copy()
        df.reset_index(drop=True, inplace=True)
        print(f"After dedup & filtering: {len(df)}")

        # 2. Normalize experience strings from Rekrute/MarocAnnonces
        #    e.g. "Junior (1 à 3 ans)" -> "Junior (1 a 3 ans)" for regex matching
        df['experience_demandee'] = df['experience_demandee'].fillna('')
        df['titre_poste'] = df['titre_poste'].fillna('')
        df['description'] = df['description'].fillna('')

        # 3. Extract target variable
        print("Generating target variable 'Niveau_du_poste'...")
        df['Niveau_du_poste'] = df.apply(self.label_job_level, axis=1)
        print("Distribution of Target:")
        print(df['Niveau_du_poste'].value_counts())

        # 4. Clean and process text
        print("Cleaning text columns (NLP)...")
        df['description_clean'] = df['description'].apply(self.clean_text)
        df['titre_clean'] = df['titre_poste'].apply(self.clean_text)

        # 5. Feature engineering
        print("Extracting technology flags and engineered features...")
        df = self.extract_features(df)

        # Save
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        df.to_csv(output_csv, index=False, encoding='utf-8-sig')
        print(f"Preprocessed data saved to: {output_csv} ({len(df)} rows)")

        return df


if __name__ == "__main__":
    cleaner = DataCleaner()
    cleaner.process()
