import os
import joblib
import pandas as pd
from src.preprocessing.clean_data import DataCleaner

class JobLevelPredictor:
    def __init__(self, model_path="models_saved/job_level_model.pkl"):
        self.model_path = model_path
        self.cleaner = DataCleaner()
        
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Saved model pipeline not found at {self.model_path}. Please run train.py first.")
            
        print(f"Loading model pipeline from {self.model_path}...")
        self.pipeline = joblib.load(self.model_path)

    def predict(self, title, description):
        """Clean input text, construct features, and predict job level."""
        # 1. Preprocess and clean inputs
        cleaned_title = self.cleaner.clean_text(title)
        cleaned_desc = self.cleaner.clean_text(description)
        
        # Create a single row DataFrame to run through feature extraction
        raw_df = pd.DataFrame([{
            'titre_poste': title,
            'description': description,
            'experience_demandee': None  # Not strictly required since we rely on description/title keywords or heuristics
        }])
        
        # 2. Extract engineered features
        feat_df = self.cleaner.extract_features(raw_df)
        
        # Add clean text columns
        feat_df['titre_clean'] = cleaned_title
        feat_df['description_clean'] = cleaned_desc
        
        # 3. Predict using pipeline
        pred_label = self.pipeline.predict(feat_df)[0]
        
        # Get probability scores if the model supports it
        try:
            probs = self.pipeline.predict_proba(feat_df)[0]
            classes = self.pipeline.classes_
            prob_dict = {classes[i]: probs[i] for i in range(len(classes))}
        except Exception:
            prob_dict = None
            
        return {
            'predicted_level': pred_label,
            'probabilities': prob_dict
        }

if __name__ == "__main__":
    # Test prediction
    import sys
    
    test_title = "Développeur Java Spring Boot Junior"
    test_desc = """
    Nous recherchons un développeur Java débutant ou stagiaire pour rejoindre notre équipe à Casablanca.
    Vous travaillerez avec Spring Boot, Hibernate et Angular.
    Connaissance de SQL et Git est un plus.
    Débutant accepté.
    """
    
    try:
        predictor = JobLevelPredictor()
        res = predictor.predict(test_title, test_desc)
        print(f"Title: {test_title}")
        print(f"Prediction: {res['predicted_level']}")
        if res['probabilities']:
            print("Probabilities:")
            for k, v in res['probabilities'].items():
                print(f"  {k}: {v:.4f}")
    except Exception as e:
        print(f"Prediction test error (model might not be trained yet): {e}")
