import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

def train_crowd_model():
    # 1. Load data
    data_path = 'bhandara_radar/ml_engine/bhandara_training_data.csv'
    df = pd.read_csv(data_path)
    
    # 2. Features (X) and Target (y)
    X = df[['hour', 'day_of_week', 'area_score']]
    y = df['crowd_level']
    
    # 3. Initialize and Train Random Forest
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    # 4. Save the model to a file
    model_path = 'bhandara_radar/ml_engine/crowd_model.joblib'
    joblib.dump(model, model_path)
    print(f"🚀 Random Forest Model trained and saved to {model_path}")

if __name__ == "__main__":
    train_crowd_model()