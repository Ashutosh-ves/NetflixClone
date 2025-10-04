import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
import joblib

# Load preprocessed data from Day 1
processed_df = pd.read_csv('movies_preprocessed.csv', low_memory=False)

# Fix data types - convert boolean strings to numeric
processed_df['adult'] = processed_df['adult'].map({'True': 1, 'False': 0, True: 1, False: 0})

# Combine overview and title for TF-IDF
text_data = processed_df['overview'].fillna('') + ' ' + processed_df['original_title'].fillna('')

# TF-IDF vectorization
tfidf = TfidfVectorizer(max_features=200, stop_words='english')
text_features = tfidf.fit_transform(text_data).toarray()

# Extract preprocessed numeric/categorical features (excluding text and identifiers)
non_text_features = processed_df.drop(columns=['id', 'original_title', 'overview'])

# Ensure all features are numeric and handle missing values
non_text_features = non_text_features.select_dtypes(include=[np.number])
non_text_features = non_text_features.fillna(0)  # Fill NaN with 0

# Combine all features
X = np.hstack([text_features, non_text_features.values])

# Train KNN model
knn = NearestNeighbors(n_neighbors=6, metric='euclidean')
knn.fit(X)

# Save models
joblib.dump(knn, 'knn_model.joblib')
joblib.dump(tfidf, 'tfidf_vectorizer.joblib')

# Recommendation function
def recommend(movie_index):
    distances, indices = knn.kneighbors([X[movie_index]])
    recommended_indices = indices[0][1:]
    return processed_df.iloc[recommended_indices][['original_title', 'overview']]

# Example: recommend based on first movie
movie_idx = 0
print("Selected:", processed_df.iloc[movie_idx]['original_title'])
print("Recommendations:")
print(recommend(movie_idx))