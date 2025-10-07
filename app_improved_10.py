from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Load the improved models with 10 recommendations
def load_models():
    """Load improved models with 10 recommendations"""
    try:
        print("Loading improved KNN model (10 recommendations)...")
        knn_model = joblib.load('improved_knn_model_10.joblib')
        print("✅ Improved KNN model with 10 recommendations loaded")
        
        print("Loading improved TF-IDF vectorizer...")
        tfidf_vectorizer = joblib.load('improved_tfidf_vectorizer_10.joblib')
        print("✅ Improved TF-IDF vectorizer loaded")
        
        print("Loading improved scaler...")
        scaler = joblib.load('improved_scaler_10.joblib')
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
        
        print("✅ Improved models with 10 recommendations loaded successfully!")
        return knn_model, tfidf_vectorizer, movies_df, X, scaler
        
    except Exception as e:
        print(f"❌ Error loading improved models: {e}")
        print("💡 Try running: python retrain_improved_model_10.py")
        return None, None, None, None, None

# Helper function to get poster URL with fallbacks
def get_poster_url(row, title):
    """Get poster URL with multiple fallback options"""
    # First try TMDB poster path
    if pd.notna(row.get('poster_path')):
        return f"https://image.tmdb.org/t/p/w500{row['poster_path']}"
    
    # Fallback: Generate poster from title using a different service
    if title and title != "Unknown Title":
        # Use a more reliable placeholder service with movie title
        clean_title = title.replace(' ', '+').replace(':', '').replace('&', 'and')
        return f"https://via.placeholder.com/300x450/1a1a2e/ffffff?text={clean_title[:20]}"
    
    # Final fallback
    return "https://via.placeholder.com/300x450/1a1a2e/ffffff?text=No+Poster"

def filter_movies_with_posters(movies_df, limit=50):
    """Filter movies that have poster paths for better user experience"""
    # First try to get movies with poster paths
    movies_with_posters = movies_df[movies_df['poster_path'].notna()]
    
    if len(movies_with_posters) >= limit:
        return movies_with_posters.head(limit)
    else:
        # If not enough movies with posters, include some without
        return movies_df.head(limit)

# Load models
knn_model, tfidf_vectorizer, movies_df, X, scaler = load_models()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api')
def api_info():
    return jsonify({"message": "Improved Movie Recommendation API with 10 recommendations is running!"})

@app.route('/api/movies', methods=['GET'])
def get_movies():
    """Get all movies with basic info"""
    if movies_df is None:
        return jsonify({"movies": []})
    
    # Return movies with posters prioritized
    filtered_movies = filter_movies_with_posters(movies_df, 50)
    movies_list = []
    for idx, row in filtered_movies.iterrows():
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
        
        # Get poster URL with fallback
        poster_url = get_poster_url(row, str(title))
        
        # Safely convert ID to integer
        try:
            movie_id_val = int(float(str(row.get('id', idx))))
        except (ValueError, TypeError):
            movie_id_val = idx
            
        movies_list.append({
            "id": movie_id_val,
            "title": str(title),
            "overview": str(overview),
            "year": year,
            "genre": "drama",  # Default genre since we don't have genre data
            "img": poster_url
        })
    
    return jsonify({"movies": movies_list})

@app.route('/api/search', methods=['GET'])
def search_movies():
    """Search movies by title"""
    query = request.args.get('q', '').lower()
    
    if movies_df is None:
        return jsonify({"movies": []})
    
    if not query:
        return jsonify({"movies": []})
    
    # Filter movies by title
    filtered_movies = movies_df[movies_df['original_title'].str.lower().str.contains(query, na=False)]
    
    movies_list = []
    for idx, row in filtered_movies.head(20).iterrows():
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
        
        # Get poster URL with fallback
        poster_url = get_poster_url(row, str(title))
        
        # Safely convert ID to integer
        try:
            movie_id_val = int(float(str(row.get('id', idx))))
        except (ValueError, TypeError):
            movie_id_val = idx
            
        movies_list.append({
            "id": movie_id_val,
            "title": str(title),
            "overview": str(overview),
            "year": year,
            "genre": "drama",
            "img": poster_url
        })
    
    return jsonify({"movies": movies_list})

@app.route('/api/movie/<int:movie_id>', methods=['GET'])
def get_movie_details(movie_id):
    """Get details for a specific movie"""
    if movies_df is None:
        return jsonify({"error": "Movies data not loaded"}), 500
    
    try:
        # Find movie by ID
        movie_row = None
        for idx, row in movies_df.iterrows():
            try:
                row_id = int(float(str(row.get('id', idx))))
                if row_id == movie_id:
                    movie_row = row
                    break
            except (ValueError, TypeError):
                continue
        
        if movie_row is None:
            return jsonify({"error": f"Movie with ID {movie_id} not found"}), 404
        
        # Handle NaN values properly
        overview = movie_row['overview'] if pd.notna(movie_row['overview']) else "No overview available"
        title = movie_row['original_title'] if pd.notna(movie_row['original_title']) else "Unknown Title"
        
        # Extract year from release_date
        year = 2000  # default
        if pd.notna(movie_row.get('release_date')):
            try:
                year_str = str(movie_row['release_date'])[:4]
                year = int(year_str) if year_str.isdigit() else 2000
            except:
                year = 2000
        
        # Get genres for this movie
        genre_columns = ['Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Documentary', 
                        'Drama', 'Family', 'Fantasy', 'Horror', 'Music', 'Mystery', 
                        'Romance', 'Science Fiction', 'Thriller', 'War', 'Western']
        available_genres = [col for col in genre_columns if col in movies_df.columns]
        movie_genres = [genre for genre in available_genres if movie_row[genre] == 1]
        
        # Get poster URL with fallback
        poster_url = get_poster_url(movie_row, str(title))
        
        # Safely convert ID to integer
        try:
            movie_id_val = int(float(str(movie_row.get('id', movie_id))))
        except (ValueError, TypeError):
            movie_id_val = movie_id
        
        movie_details = {
            "id": movie_id_val,
            "title": str(title),
            "overview": str(overview),
            "year": year,
            "genres": movie_genres,
            "img": poster_url,
            "budget": float(movie_row.get('budget_norm', 0)) if pd.notna(movie_row.get('budget_norm')) else 0,
            "adult": bool(movie_row.get('adult', False))
        }
        
        return jsonify({"movie": movie_details})
        
    except Exception as e:
        print(f"Movie details error: {e}")
        return jsonify({"error": f"Failed to get movie details: {str(e)}"}), 500

@app.route('/api/recommend/<int:movie_id>', methods=['GET'])
def recommend_movies(movie_id):
    """Get 10 improved recommendations for a specific movie"""
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
                # If ID conversion fails, skip this row
                continue
        
        if movie_idx is None:
            return jsonify({"error": f"Movie with ID {movie_id} not found"}), 404
        
        print(f"Finding 10 recommendations for: {movie_row['original_title']}")
        
        # Get 10 recommendations using improved model
        distances, indices = knn_model.kneighbors([X[movie_idx]])
        recommended_indices = indices[0][1:]  # Exclude the movie itself (now 10 recommendations)
        
        # Convert cosine distances to similarity scores (cosine distance = 1 - cosine similarity)
        similarities = 1 - distances[0][1:]
        
        recommendations = []
        for i, idx in enumerate(recommended_indices):
            row = movies_df.iloc[idx]
            
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
            
            # Use improved similarity score from cosine similarity
            similarity_score = float(similarities[i])
            
            # Get poster URL with fallback
            poster_url = get_poster_url(row, str(title))
            
            # Safely convert ID to integer
            try:
                movie_id_val = int(float(str(row.get('id', idx))))
            except (ValueError, TypeError):
                movie_id_val = idx
            
            recommendations.append({
                "id": movie_id_val,
                "title": str(title),
                "overview": str(overview),
                "year": year,
                "genre": "drama",
                "similarity_score": similarity_score,
                "img": poster_url
            })
        
        selected_movie_title = str(movie_row['original_title']) if pd.notna(movie_row['original_title']) else "Unknown Title"
        
        print(f"✅ Found 10 recommendations for {selected_movie_title}")
        
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
    """Get popular movies for better recommendations"""
    if movies_df is None:
        return jsonify({"movies": []})
    
    try:
        # Get movies with good titles and preferably with posters
        popular_movies = movies_df.head(500)
        popular_movies = popular_movies[popular_movies['original_title'].notna()]
        
        # Prioritize movies with poster paths
        movies_with_posters = popular_movies[popular_movies['poster_path'].notna()]
        
        if len(movies_with_posters) >= 6:
            sampled = movies_with_posters.sample(n=6)
        else:
            # If not enough movies with posters, mix with others
            sample_size = min(6, len(popular_movies))
            sampled = popular_movies.sample(n=sample_size)
        
        movies_list = []
        for idx, row in sampled.iterrows():
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
            
            # Get poster URL with fallback
            poster_url = get_poster_url(row, str(title))
            
            # Safely convert ID to integer
            try:
                movie_id_val = int(float(str(row.get('id', idx))))
            except (ValueError, TypeError):
                movie_id_val = idx
                
            movies_list.append({
                "id": movie_id_val,
                "title": str(title),
                "overview": str(overview),
                "year": year,
                "genre": "drama",
                "img": poster_url
            })
        
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
        # Pick a random popular movie (from first 1000 to get better known movies)
        random_idx = np.random.randint(0, min(1000, len(movies_df)))
        movie_row = movies_df.iloc[random_idx]
        movie_id = int(movie_row.get('id', random_idx))
        
        return recommend_movies(movie_id)
    except Exception as e:
        print(f"Error in random recommendations: {e}")
        return jsonify({"error": f"Random recommendation failed: {str(e)}"}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 IMPROVED MOVIE RECOMMENDATION SYSTEM WITH 10 RECOMMENDATIONS")
    print("="*60)
    print("This version provides 10 high-quality recommendations using:")
    print("  • Cosine similarity for better accuracy")
    print("  • Weighted features (genres prioritized)")
    print("  • Advanced TF-IDF with bigrams")
    print("  • Proper feature scaling")
    print("Run on port 5002 to test alongside other versions")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5002)  # Different port