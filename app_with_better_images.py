from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
import os
from improved_image_handler import MovieImageHandler

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Initialize the enhanced image handler
image_handler = MovieImageHandler()

# Load the improved models
def load_models():
    """Load improved models with better error handling"""
    try:
        print("Loading improved KNN model...")
        knn_model = joblib.load('improved_knn_model.joblib')
        print("✅ Improved KNN model loaded")
        
        print("Loading improved TF-IDF vectorizer...")
        tfidf_vectorizer = joblib.load('improved_tfidf_vectorizer.joblib')
        print("✅ Improved TF-IDF vectorizer loaded")
        
        print("Loading improved scaler...")
        scaler = joblib.load('improved_scaler.joblib')
        print("✅ Improved scaler loaded")
        
        print("Loading movie data...")
        movies_df = pd.read_csv('movies_preprocessed.csv', low_memory=False)
        
        # Load original metadata for poster paths
        print("Loading poster data...")
        original_df = pd.read_csv('movies_metadata.csv', low_memory=False)
        # Merge poster paths
        movies_df = movies_df.merge(original_df[['id', 'poster_path', 'release_date']], on='id', how='left', suffixes=('', '_orig'))
        
        print(f"✅ Loaded {len(movies_df)} movies with poster data")
        
        # Preprocess the data (same as in improved_model.py)
        movies_df['adult'] = movies_df['adult'].map({'True': 1, 'False': 0, True: 1, False: 0})
        text_data = movies_df['overview'].fillna('') + ' ' + movies_df['original_title'].fillna('')
        
        # Improved TF-IDF with same parameters as training
        text_features = tfidf_vectorizer.transform(text_data).toarray()
        
        # Extract genre features
        genre_columns = ['Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Documentary', 
                        'Drama', 'Family', 'Fantasy', 'Horror', 'Music', 'Mystery', 
                        'Romance', 'Science Fiction', 'Thriller', 'War', 'Western']
        available_genres = [col for col in genre_columns if col in movies_df.columns]
        genre_features = movies_df[available_genres].fillna(0).values
        
        # Extract language features
        language_columns = [col for col in movies_df.columns if col in ['en', 'fr', 'es', 'de', 'it', 'ja', 'ko', 'zh']]
        language_features = movies_df[language_columns].fillna(0).values if language_columns else np.zeros((len(movies_df), 1))
        
        # Extract and scale numerical features
        numerical_features = movies_df[['budget_norm', 'adult']].fillna(0).values
        numerical_features_scaled = scaler.transform(numerical_features)
        
        # Apply same weights as in training
        text_weight = 1.0
        genre_weight = 3.0
        language_weight = 0.5
        numerical_weight = 0.5
        
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
        
        print("✅ Improved models and data loaded successfully!")
        return knn_model, tfidf_vectorizer, movies_df, X, scaler, available_genres
        
    except Exception as e:
        print(f"❌ Error loading improved models: {e}")
        print("💡 Try running: python improved_model.py")
        return None, None, None, None, None, None

def get_movie_genres(row, available_genres):
    """Extract genres for a movie row"""
    return [genre for genre in available_genres if row[genre] == 1]

def get_enhanced_poster_url(row, title, available_genres, year=None):
    """Get enhanced poster URL using the improved image handler"""
    # Get genres for this movie
    genres = get_movie_genres(row, available_genres)
    
    # Use the enhanced image handler
    return image_handler.get_movie_poster(row, title, genres, year)

def create_movie_dict(row, idx, available_genres):
    """Create a standardized movie dictionary with enhanced images"""
    # Handle NaN values properly
    overview = row['overview'] if pd.notna(row['overview']) else "No overview available"
    title = row['original_title'] if pd.notna(row['original_title']) else "Unknown Title"
    
    # Truncate overview if too long
    if len(str(overview)) > 200:
        overview = str(overview)[:200] + "..."
    
    # Extract year from release_date
    year = 2000  # default
    if pd.notna(row.get('release_date')):
        try:
            year_str = str(row['release_date'])[:4]
            year = int(year_str) if year_str.isdigit() else 2000
        except:
            year = 2000
    
    # Get enhanced poster URL
    poster_url = get_enhanced_poster_url(row, str(title), available_genres, year)
    
    # Get genres
    genres = get_movie_genres(row, available_genres)
    
    # Safely convert ID to integer
    try:
        movie_id_val = int(float(str(row.get('id', idx))))
    except (ValueError, TypeError):
        movie_id_val = idx
    
    return {
        "id": movie_id_val,
        "title": str(title),
        "overview": str(overview),
        "year": year,
        "genres": genres,
        "genre": genres[0] if genres else "drama",  # Primary genre for compatibility
        "img": poster_url
    }

# Load models
knn_model, tfidf_vectorizer, movies_df, X, scaler, available_genres = load_models()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api')
def api_info():
    return jsonify({
        "message": "Enhanced Movie Recommendation API with Better Images is running!",
        "features": [
            "Genre-based poster colors",
            "Multiple fallback strategies",
            "Enhanced placeholder generation",
            "Improved visual experience"
        ]
    })

@app.route('/api/movies', methods=['GET'])
def get_movies():
    """Get all movies with enhanced images"""
    if movies_df is None:
        return jsonify({"movies": []})
    
    # Return first 50 movies with enhanced images
    movies_list = []
    for idx, row in movies_df.head(50).iterrows():
        movie_dict = create_movie_dict(row, idx, available_genres)
        movies_list.append(movie_dict)
    
    return jsonify({"movies": movies_list})

@app.route('/api/search', methods=['GET'])
def search_movies():
    """Search movies by title with enhanced images"""
    query = request.args.get('q', '').lower()
    
    if movies_df is None:
        return jsonify({"movies": []})
    
    if not query:
        return jsonify({"movies": []})
    
    # Filter movies by title
    filtered_movies = movies_df[movies_df['original_title'].str.lower().str.contains(query, na=False)]
    
    movies_list = []
    for idx, row in filtered_movies.head(20).iterrows():
        movie_dict = create_movie_dict(row, idx, available_genres)
        movies_list.append(movie_dict)
    
    return jsonify({"movies": movies_list})

@app.route('/api/movie/<int:movie_id>', methods=['GET'])
def get_movie_details(movie_id):
    """Get details for a specific movie with enhanced images"""
    if movies_df is None:
        return jsonify({"error": "Movies data not loaded"}), 500
    
    try:
        # Find movie by ID
        movie_row = None
        movie_idx = None
        for idx, row in movies_df.iterrows():
            try:
                row_id = int(float(str(row.get('id', idx))))
                if row_id == movie_id:
                    movie_row = row
                    movie_idx = idx
                    break
            except (ValueError, TypeError):
                continue
        
        if movie_row is None:
            return jsonify({"error": f"Movie with ID {movie_id} not found"}), 404
        
        # Create detailed movie dictionary
        movie_dict = create_movie_dict(movie_row, movie_idx, available_genres)
        
        # Add additional details
        movie_dict.update({
            "budget": float(movie_row.get('budget_norm', 0)) if pd.notna(movie_row.get('budget_norm')) else 0,
            "adult": bool(movie_row.get('adult', False))
        })
        
        return jsonify({"movie": movie_dict})
        
    except Exception as e:
        print(f"Movie details error: {e}")
        return jsonify({"error": f"Failed to get movie details: {str(e)}"}), 500

@app.route('/api/recommend/<int:movie_id>', methods=['GET'])
def recommend_movies(movie_id):
    """Get recommendations with enhanced images"""
    if knn_model is None or movies_df is None or X is None:
        return jsonify({"error": "Models not loaded"}), 500
    
    try:
        # Find movie index by ID
        movie_idx = None
        movie_row = None
        for idx, row in movies_df.iterrows():
            try:
                row_id = int(float(str(row.get('id', idx))))
                if row_id == movie_id:
                    movie_idx = idx
                    movie_row = row
                    break
            except (ValueError, TypeError):
                continue
        
        if movie_idx is None:
            return jsonify({"error": f"Movie with ID {movie_id} not found"}), 404
        
        print(f"Finding recommendations for: {movie_row['original_title']}")
        
        # Get recommendations using improved model
        distances, indices = knn_model.kneighbors([X[movie_idx]])
        recommended_indices = indices[0][1:]  # Exclude the movie itself
        
        # Convert cosine distances to similarity scores
        similarities = 1 - distances[0][1:]
        
        recommendations = []
        for i, idx in enumerate(recommended_indices):
            row = movies_df.iloc[idx]
            
            # Create movie dictionary with enhanced images
            movie_dict = create_movie_dict(row, idx, available_genres)
            
            # Add similarity score
            movie_dict["similarity_score"] = float(similarities[i])
            
            recommendations.append(movie_dict)
        
        selected_movie_title = str(movie_row['original_title']) if pd.notna(movie_row['original_title']) else "Unknown Title"
        
        return jsonify({
            "movie": {
                "id": movie_id,
                "title": selected_movie_title
            },
            "recommendations": recommendations
        })
        
    except Exception as e:
        print(f"Recommendation error: {e}")
        return jsonify({"error": f"Recommendation failed: {str(e)}"}), 500

@app.route('/api/popular', methods=['GET'])
def get_popular_movies():
    """Get popular movies with enhanced images"""
    if movies_df is None:
        return jsonify({"movies": []})
    
    try:
        # Get movies with good titles
        popular_movies = movies_df.head(500)
        popular_movies = popular_movies[popular_movies['original_title'].notna()]
        
        # Sample 6 movies
        sample_size = min(6, len(popular_movies))
        sampled = popular_movies.sample(n=sample_size)
        
        movies_list = []
        for idx, row in sampled.iterrows():
            movie_dict = create_movie_dict(row, idx, available_genres)
            movies_list.append(movie_dict)
        
        return jsonify({"movies": movies_list})
        
    except Exception as e:
        print(f"Popular movies error: {e}")
        return jsonify({"movies": []})

@app.route('/api/recommend/random', methods=['GET'])
def recommend_random():
    """Get recommendations for a random movie"""
    if movies_df is None or knn_model is None:
        return jsonify({"error": "Models not loaded"}), 500
    
    try:
        # Pick a random popular movie
        random_idx = np.random.randint(0, min(1000, len(movies_df)))
        movie_row = movies_df.iloc[random_idx]
        movie_id = int(movie_row.get('id', random_idx))
        
        return recommend_movies(movie_id)
    except Exception as e:
        print(f"Error in random recommendations: {e}")
        return jsonify({"error": f"Random recommendation failed: {str(e)}"}), 500

@app.route('/api/image-stats', methods=['GET'])
def get_image_stats():
    """Get statistics about image availability"""
    if movies_df is None:
        return jsonify({"error": "Movies data not loaded"}), 500
    
    total_movies = len(movies_df)
    movies_with_posters = len(movies_df[movies_df['poster_path'].notna()])
    movies_without_posters = total_movies - movies_with_posters
    
    return jsonify({
        "total_movies": total_movies,
        "movies_with_tmdb_posters": movies_with_posters,
        "movies_without_posters": movies_without_posters,
        "poster_coverage": f"{(movies_with_posters/total_movies)*100:.1f}%",
        "fallback_strategies": [
            "TMDB poster paths",
            "Genre-based colored placeholders", 
            "Title-based placeholders",
            "Random scenic images"
        ]
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🖼️  ENHANCED MOVIE RECOMMENDATION SYSTEM WITH BETTER IMAGES")
    print("="*60)
    print("New image features:")
    print("  • Genre-based poster colors")
    print("  • Multiple fallback strategies")
    print("  • Enhanced placeholder generation")
    print("  • Better visual experience")
    print("Run on port 5003 to test enhanced images")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5003)