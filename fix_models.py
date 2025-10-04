#!/usr/bin/env python3
"""
Quick fix for model compatibility issues
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import joblib
import os

print("🔧 Quick Model Fix")
print("=" * 20)

# Check if files exist
if not os.path.exists('movies_preprocessed.csv'):
    print("❌ movies_preprocessed.csv not found")
    exit(1)

print("📊 Loading data...")
df = pd.read_csv('movies_preprocessed.csv', low_memory=False)
print(f"✅ Loaded {len(df)} movies")

# Quick preprocessing
df['adult'] = df['adult'].map({'True': 1, 'False': 0, True: 1, False: 0})
text_data = df['overview'].fillna('') + ' ' + df['original_title'].fillna('')

print("🔤 Creating features...")
tfidf = TfidfVectorizer(max_features=200, stop_words='english')
text_features = tfidf.fit_transform(text_data).toarray()

non_text_features = df.drop(columns=['id', 'original_title', 'overview'])
non_text_features = non_text_features.select_dtypes(include=[np.number])
non_text_features = non_text_features.fillna(0)

X = np.hstack([text_features, non_text_features.values])

print("🤖 Training model...")
knn = NearestNeighbors(n_neighbors=6, metric='euclidean')
knn.fit(X)

print("💾 Saving models...")
joblib.dump(knn, 'knn_model.joblib')
joblib.dump(tfidf, 'tfidf_vectorizer.joblib')

print("✅ Done! Models fixed and saved.")
print("Now run: python app.py")