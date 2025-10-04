#!/usr/bin/env python3
"""
Retrain the KNN models with current scikit-learn version to fix compatibility issues
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import joblib
import os

def retrain_models():
    """Retrain the models with current environment"""
    print("🔄 Retraining models with current scikit-learn version...")
    
    # Check if preprocessed data exists
    if not os.path.exists('movies_preprocessed.csv'):
        print("❌ movies_preprocessed.csv not found. Please run preprocessing first.")
        return False
    
    try:
        # Load preprocessed data
        print("📊 Loading preprocessed data...")
        processed_df = pd.read_csv('movies_preprocessed.csv', low_memory=False)
        print(f"✅ Loaded {len(processed_df)} movies")
        
        # Fix data types - convert boolean strings to numeric
        processed_df['adult'] = processed_df['adult'].map({'True': 1, 'False': 0, True: 1, False: 0})
        
        # Combine overview and title for TF-IDF
        print("🔤 Creating text features...")
        text_data = processed_df['overview'].fillna('') + ' ' + processed_df['original_title'].fillna('')
        
        # TF-IDF vectorization
        tfidf = TfidfVectorizer(max_features=200, stop_words='english')
        text_features = tfidf.fit_transform(text_data).toarray()
        print(f"✅ Created {text_features.shape[1]} text features")
        
        # Extract preprocessed numeric/categorical features (excluding text and identifiers)
        print("🔢 Processing numeric features...")
        non_text_features = processed_df.drop(columns=['id', 'original_title', 'overview'])
        
        # Ensure all features are numeric and handle missing values
        non_text_features = non_text_features.select_dtypes(include=[np.number])
        non_text_features = non_text_features.fillna(0)  # Fill NaN with 0
        print(f"✅ Created {non_text_features.shape[1]} numeric features")
        
        # Combine all features
        X = np.hstack([text_features, non_text_features.values])
        print(f"✅ Combined feature matrix: {X.shape}")
        
        # Train KNN model
        print("🤖 Training KNN model...")
        knn = NearestNeighbors(n_neighbors=6, metric='euclidean')
        knn.fit(X)
        print("✅ KNN model trained successfully")
        
        # Save models
        print("💾 Saving models...")
        joblib.dump(knn, 'knn_model.joblib')
        joblib.dump(tfidf, 'tfidf_vectorizer.joblib')
        print("✅ Models saved successfully")
        
        # Test the model
        print("🧪 Testing model...")
        movie_idx = 0
        distances, indices = knn.kneighbors([X[movie_idx]])
        recommended_indices = indices[0][1:]
        
        selected_movie = processed_df.iloc[movie_idx]['original_title']
        recommendations = processed_df.iloc[recommended_indices]['original_title'].tolist()
        
        print(f"✅ Test successful!")
        print(f"   Selected: {selected_movie}")
        print(f"   Recommendations: {recommendations[:3]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error retraining models: {e}")
        return False

if __name__ == "__main__":
    print("🎬 CodeFlix Model Retraining")
    print("=" * 35)
    
    if retrain_models():
        print("\n🎉 Models retrained successfully!")
        print("You can now start the backend with: python app.py")
    else:
        print("\n❌ Model retraining failed!")
        print("Please check the error messages above.")