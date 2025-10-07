import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import joblib

print("Loading preprocessed data...")
processed_df = pd.read_csv('movies_preprocessed.csv', low_memory=False)

# Fix data types - convert boolean strings to numeric
processed_df['adult'] = processed_df['adult'].map({'True': 1, 'False': 0, True: 1, False: 0})

print(f"Loaded {len(processed_df)} movies")

# Combine overview and title for TF-IDF with better parameters
text_data = processed_df['overview'].fillna('') + ' ' + processed_df['original_title'].fillna('')

# Improved TF-IDF with more features and better parameters
tfidf = TfidfVectorizer(
    max_features=500,  # Increased from 200
    stop_words='english',
    ngram_range=(1, 2),  # Include bigrams for better context
    min_df=2,  # Ignore terms that appear in less than 2 documents
    max_df=0.8  # Ignore terms that appear in more than 80% of documents
)
text_features = tfidf.fit_transform(text_data).toarray()

print(f"TF-IDF features shape: {text_features.shape}")

# Extract genre features (these are the most important for movie similarity)
genre_columns = ['Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Documentary', 
                'Drama', 'Family', 'Fantasy', 'Horror', 'Music', 'Mystery', 
                'Romance', 'Science Fiction', 'Thriller', 'War', 'Western']

# Get available genre columns (some might not exist in your data)
available_genres = [col for col in genre_columns if col in processed_df.columns]
print(f"Available genres: {available_genres}")

genre_features = processed_df[available_genres].fillna(0).values

# Extract other categorical features (languages) - but limit to most common ones
language_columns = [col for col in processed_df.columns if col in ['en', 'fr', 'es', 'de', 'it', 'ja', 'ko', 'zh']]
language_features = processed_df[language_columns].fillna(0).values if language_columns else np.zeros((len(processed_df), 1))

# Extract numerical features
numerical_features = processed_df[['budget_norm', 'adult']].fillna(0).values

# Scale numerical features
scaler = StandardScaler()
numerical_features_scaled = scaler.fit_transform(numerical_features)

print(f"Feature shapes:")
print(f"  Text features: {text_features.shape}")
print(f"  Genre features: {genre_features.shape}")
print(f"  Language features: {language_features.shape}")
print(f"  Numerical features: {numerical_features_scaled.shape}")

# Combine features with different weights to prioritize genres and content
# Weight genres more heavily since they're most important for movie similarity
text_weight = 1.0
genre_weight = 3.0  # Give genres 3x more importance
language_weight = 0.5
numerical_weight = 0.5

# Apply weights
weighted_text = text_features * text_weight
weighted_genres = genre_features * genre_weight
weighted_languages = language_features * language_weight
weighted_numerical = numerical_features_scaled * numerical_weight

# Combine all features
X = np.hstack([
    weighted_text,
    weighted_genres, 
    weighted_languages,
    weighted_numerical
])

print(f"Final feature matrix shape: {X.shape}")

# Use cosine similarity instead of euclidean distance for better results with mixed features
# Increased to 11 neighbors (10 recommendations + 1 original movie to exclude)
knn = NearestNeighbors(n_neighbors=11, metric='cosine')
knn.fit(X)

# Save improved models
joblib.dump(knn, 'improved_knn_model.joblib')
joblib.dump(tfidf, 'improved_tfidf_vectorizer.joblib')
joblib.dump(scaler, 'improved_scaler.joblib')

print("✅ Improved models saved!")

# Improved recommendation function
def recommend_improved(movie_index, n_recommendations=10):
    """Get improved recommendations using cosine similarity"""
    distances, indices = knn.kneighbors([X[movie_index]])
    recommended_indices = indices[0][1:]  # Exclude the movie itself
    
    # Convert cosine distances to similarity scores (cosine distance = 1 - cosine similarity)
    similarities = 1 - distances[0][1:]
    
    recommendations = []
    for i, idx in enumerate(recommended_indices):
        movie_data = processed_df.iloc[idx]
        recommendations.append({
            'title': movie_data['original_title'],
            'overview': movie_data['overview'][:200] + '...' if len(str(movie_data['overview'])) > 200 else movie_data['overview'],
            'similarity_score': float(similarities[i]),
            'genres': [col for col in available_genres if movie_data[col] == 1]
        })
    
    return recommendations

# Test with Toy Story
print("\n" + "="*50)
print("TESTING IMPROVED RECOMMENDATIONS")
print("="*50)

# Find Toy Story
toy_story_idx = None
for idx, row in processed_df.iterrows():
    if 'Toy Story' in str(row['original_title']) and '2' not in str(row['original_title']) and '3' not in str(row['original_title']):
        toy_story_idx = idx
        break

if toy_story_idx is not None:
    print(f"\nSelected movie: {processed_df.iloc[toy_story_idx]['original_title']}")
    print(f"Genres: {[col for col in available_genres if processed_df.iloc[toy_story_idx][col] == 1]}")
    
    print(f"\nImproved Recommendations:")
    recommendations = recommend_improved(toy_story_idx)
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['title']}")
        print(f"   Similarity: {rec['similarity_score']:.3f}")
        print(f"   Genres: {rec['genres']}")
        print(f"   Overview: {rec['overview']}")
        print()
else:
    print("Toy Story not found in dataset")

print("✅ Improved model training complete!")