import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances

def explain_feature_combination():
    """Explain how different feature types are combined in the movie recommendation system"""
    
    print("🎬 HOW MOVIE RECOMMENDATION FEATURES ARE COMBINED")
    print("=" * 60)
    
    # Sample movies for demonstration
    movies_data = {
        'title': ['Toy Story', 'The Dark Knight', 'Titanic'],
        'overview': [
            'A cowboy doll is profoundly threatened when a new spaceman figure supplants him as top toy',
            'Batman raises the stakes in his war on crime with the help of Lt. Jim Gordon and District Attorney Harvey Dent',
            'A seventeen-year-old aristocrat falls in love with a kind but poor artist aboard the luxurious ill-fated R.M.S. Titanic'
        ],
        'budget_norm': [0.3, 0.8, 0.9],  # Normalized budget
        'adult': [0, 0, 0],              # Adult content flag
        'Animation': [1, 0, 0],          # Genre: Animation
        'Action': [0, 1, 0],             # Genre: Action  
        'Romance': [0, 0, 1],            # Genre: Romance
        'Comedy': [1, 0, 0],             # Genre: Comedy
        'Drama': [0, 1, 1],              # Genre: Drama
        'en': [1, 1, 1],                 # Language: English
        'fr': [0, 0, 0],                 # Language: French
    }
    
    df = pd.DataFrame(movies_data)
    
    print("📊 SAMPLE MOVIES:")
    for i, row in df.iterrows():
        genres = [col for col in ['Animation', 'Action', 'Romance', 'Comedy', 'Drama'] if row[col] == 1]
        print(f"  {i+1}. {row['title']} - Genres: {genres}, Budget: {row['budget_norm']}")
    
    print(f"\n🔤 STEP 1: TEXT FEATURES (TF-IDF VECTORS)")
    print("-" * 40)
    
    # Create TF-IDF vectors from text
    text_data = df['overview']
    tfidf = TfidfVectorizer(max_features=10, stop_words='english')  # Small for demo
    text_features = tfidf.fit_transform(text_data).toarray()
    
    print("Text data:")
    for i, text in enumerate(text_data):
        print(f"  Movie {i+1}: {text[:50]}...")
    
    print(f"\nTF-IDF feature names: {list(tfidf.get_feature_names_out())}")
    print(f"TF-IDF vectors shape: {text_features.shape}")
    print("TF-IDF vectors:")
    for i, vector in enumerate(text_features):
        print(f"  Movie {i+1}: {vector.round(3)}")
    
    print(f"\n🏷️  STEP 2: CATEGORICAL FEATURES (ONE-HOT ENCODED)")
    print("-" * 40)
    
    # Genre features (already one-hot encoded)
    genre_features = df[['Animation', 'Action', 'Romance', 'Comedy', 'Drama']].values
    print(f"Genre features shape: {genre_features.shape}")
    print("Genre vectors:")
    for i, vector in enumerate(genre_features):
        print(f"  Movie {i+1}: {vector}")
    
    # Language features
    language_features = df[['en', 'fr']].values
    print(f"\nLanguage features shape: {language_features.shape}")
    print("Language vectors:")
    for i, vector in enumerate(language_features):
        print(f"  Movie {i+1}: {vector}")
    
    print(f"\n🔢 STEP 3: NUMERICAL FEATURES (SCALED)")
    print("-" * 40)
    
    # Numerical features
    numerical_features = df[['budget_norm', 'adult']].values
    scaler = StandardScaler()
    numerical_features_scaled = scaler.fit_transform(numerical_features)
    
    print("Original numerical features:")
    for i, vector in enumerate(numerical_features):
        print(f"  Movie {i+1}: {vector}")
    
    print("Scaled numerical features (mean=0, std=1):")
    for i, vector in enumerate(numerical_features_scaled):
        print(f"  Movie {i+1}: {vector.round(3)}")
    
    print(f"\n⚖️  STEP 4: FEATURE WEIGHTING")
    print("-" * 40)
    
    # Apply weights (like in improved model)
    text_weight = 1.0
    genre_weight = 3.0      # Genres are most important
    language_weight = 0.5
    numerical_weight = 0.5
    
    weighted_text = text_features * text_weight
    weighted_genres = genre_features * genre_weight
    weighted_languages = language_features * language_weight
    weighted_numerical = numerical_features_scaled * numerical_weight
    
    print(f"Weights applied:")
    print(f"  Text weight: {text_weight}")
    print(f"  Genre weight: {genre_weight} (most important!)")
    print(f"  Language weight: {language_weight}")
    print(f"  Numerical weight: {numerical_weight}")
    
    print(f"\n🔗 STEP 5: FEATURE CONCATENATION")
    print("-" * 40)
    
    # Combine all features horizontally
    X = np.hstack([
        weighted_text,      # Shape: (3, 10)
        weighted_genres,    # Shape: (3, 5) 
        weighted_languages, # Shape: (3, 2)
        weighted_numerical  # Shape: (3, 2)
    ])
    
    print(f"Combined feature matrix shape: {X.shape}")
    print(f"Total features per movie: {X.shape[1]}")
    print(f"  - Text features: {weighted_text.shape[1]}")
    print(f"  - Genre features: {weighted_genres.shape[1]}")
    print(f"  - Language features: {weighted_languages.shape[1]}")
    print(f"  - Numerical features: {weighted_numerical.shape[1]}")
    
    print(f"\nCombined feature vectors:")
    for i, vector in enumerate(X):
        print(f"  Movie {i+1} ({df.iloc[i]['title']}): [{vector[0]:.2f}, {vector[1]:.2f}, ..., {vector[-2]:.2f}, {vector[-1]:.2f}] (showing first 2 and last 2)")
    
    print(f"\n📏 STEP 6: DISTANCE CALCULATIONS")
    print("-" * 40)
    
    # Calculate Euclidean distances
    euclidean_dist = euclidean_distances(X)
    print("Euclidean distances:")
    print("     ", "  ".join([f"M{i+1}" for i in range(3)]))
    for i, row in enumerate(euclidean_dist):
        print(f"M{i+1}: {' '.join([f'{d:.2f}' for d in row])}")
    
    # Calculate Cosine similarities
    cosine_sim = cosine_similarity(X)
    print(f"\nCosine similarities:")
    print("     ", "  ".join([f"M{i+1}" for i in range(3)]))
    for i, row in enumerate(cosine_sim):
        print(f"M{i+1}: {' '.join([f'{s:.3f}' for s in row])}")
    
    print(f"\n🎯 STEP 7: INTERPRETATION")
    print("-" * 40)
    
    print("Euclidean Distance:")
    print("  • Measures straight-line distance in feature space")
    print("  • Smaller distance = more similar movies")
    print("  • Affected by feature magnitude")
    print("  • Example: Toy Story vs Dark Knight = {:.2f}".format(euclidean_dist[0][1]))
    
    print(f"\nCosine Similarity:")
    print("  • Measures angle between feature vectors")
    print("  • Range: -1 (opposite) to 1 (identical)")
    print("  • Ignores magnitude, focuses on direction")
    print("  • Example: Toy Story vs Dark Knight = {:.3f}".format(cosine_sim[0][1]))
    
    # Find most similar movies
    print(f"\n🏆 RECOMMENDATIONS FOR TOY STORY:")
    toy_story_similarities = cosine_sim[0]  # Similarities to Toy Story
    sorted_indices = np.argsort(toy_story_similarities)[::-1][1:]  # Exclude self
    
    for i, idx in enumerate(sorted_indices):
        movie_name = df.iloc[idx]['title']
        similarity = toy_story_similarities[idx]
        print(f"  {i+1}. {movie_name} (similarity: {similarity:.3f})")
    
    return X, euclidean_dist, cosine_sim

def explain_why_cosine_better():
    """Explain why cosine similarity is better than euclidean for mixed features"""
    
    print(f"\n🤔 WHY COSINE SIMILARITY IS BETTER THAN EUCLIDEAN")
    print("=" * 60)
    
    # Example with extreme case
    print("Consider two movies with same genres but different text lengths:")
    
    # Movie A: Short description
    movie_a = np.array([0.1, 0.2, 3.0, 3.0, 3.0, 0.5, 0.5])  # [text_features, genre_features, other]
    # Movie B: Long description (higher TF-IDF values)
    movie_b = np.array([0.8, 0.9, 3.0, 3.0, 3.0, 0.5, 0.5])  # Same genres, different text
    
    # Calculate distances
    euclidean_dist = np.linalg.norm(movie_a - movie_b)
    cosine_sim = np.dot(movie_a, movie_b) / (np.linalg.norm(movie_a) * np.linalg.norm(movie_b))
    
    print(f"Movie A: {movie_a}")
    print(f"Movie B: {movie_b}")
    print(f"Same genres? YES (both have [3.0, 3.0, 3.0])")
    print(f"Euclidean distance: {euclidean_dist:.3f} (affected by text length)")
    print(f"Cosine similarity: {cosine_sim:.3f} (focuses on pattern)")
    
    print(f"\n✅ Cosine similarity recognizes they're similar despite text length differences")
    print(f"❌ Euclidean distance is misled by text magnitude differences")

if __name__ == "__main__":
    X, euclidean_dist, cosine_sim = explain_feature_combination()
    explain_why_cosine_better()
    
    print(f"\n💡 KEY TAKEAWAYS:")
    print("1. Different feature types are combined into one big vector")
    print("2. Features are weighted by importance (genres get 3x weight)")
    print("3. Cosine similarity works better for mixed feature types")
    print("4. The model finds movies with similar 'patterns' not just magnitudes")