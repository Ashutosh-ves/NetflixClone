from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Load the trained models and data
def load_models():
    """Load models with better error handling"""
    try:
        print("Loading KNN model...")
        knn_model = joblib.load('improved_knn_model.joblib')
        print("✅ KNN model loaded")
        
        print("Loading TF-IDF vectorizer...")
        tfidf_vectorizer = joblib.load('improved_tfidf_vectorizer.joblib')
        print("✅ TF-IDF vectorizer loaded")
        
        print("Loading movie data...")
        movies_df = pd.read_csv('movies_preprocessed.csv', low_memory=False)
        
        # Load original metadata for poster paths
        print("Loading poster data...")
        original_df = pd.read_csv('movies_metadata.csv', low_memory=False)
        # Merge poster paths
        movies_df = movies_df.merge(original_df[['id', 'poster_path', 'release_date']], on='id', how='left', suffixes=('', '_orig'))
        
        print(f"✅ Loaded {len(movies_df)} movies with poster data")
        
        # Preprocess the data (same as in model.py)
        movies_df['adult'] = movies_df['adult'].map({'True': 1, 'False': 0, True: 1, False: 0})
        text_data = movies_df['overview'].fillna('') + ' ' + movies_df['original_title'].fillna('')
        text_features = tfidf_vectorizer.transform(text_data).toarray()
        
        non_text_features = movies_df.drop(columns=['id', 'original_title', 'overview'])
        non_text_features = non_text_features.select_dtypes(include=[np.number])
        non_text_features = non_text_features.fillna(0)
        
        X = np.hstack([text_features, non_text_features.values])
        
        print("✅ Models and data loaded successfully!")
        return knn_model, tfidf_vectorizer, movies_df, X
        
    except Exception as e:
        print(f"❌ Error loading models: {e}")
        print("💡 Try running: python retrain_models.py")
        return None, None, None, None

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
knn_model, tfidf_vectorizer, movies_df, X = load_models()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api')
def api_info():
    return jsonify({"message": "Movie Recommendation API is running!"})

@app.route('/api/movies', methods=['GET'])
def get_movies():
    """Get all movies with basic info"""
    if movies_df is None:
        # Return mock data if models aren't loaded
        return jsonify({
            "movies": [
                {"id": 1, "title": "The Shawshank Redemption", "overview": "Two imprisoned men bond over a number of years...", "year": 1994, "genre": "drama", "img": "https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg"},
                {"id": 2, "title": "The Godfather", "overview": "The aging patriarch of an organized crime dynasty...", "year": 1972, "genre": "drama", "img": "https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg"},
                {"id": 3, "title": "The Dark Knight", "overview": "When the menace known as the Joker wreaks havoc...", "year": 2008, "genre": "action", "img": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg"},
                {"id": 4, "title": "Pulp Fiction", "overview": "The lives of two mob hitmen, a boxer, a gangster...", "year": 1994, "genre": "drama", "img": "https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg"},
                {"id": 5, "title": "Forrest Gump", "overview": "The presidencies of Kennedy and Johnson...", "year": 1994, "genre": "drama", "img": "https://image.tmdb.org/t/p/w500/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg"}
            ]
        })
    
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
        
        movies_list.append({
            "id": int(row.get('id', idx)),
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
        # Return mock search results
        mock_movies = [
            {"id": 1, "title": "The Shawshank Redemption", "overview": "Two imprisoned men bond over a number of years...", "year": 1994, "genre": "drama", "img": "https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg"},
            {"id": 2, "title": "The Godfather", "overview": "The aging patriarch of an organized crime dynasty...", "year": 1972, "genre": "drama", "img": "https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg"},
            {"id": 3, "title": "The Dark Knight", "overview": "When the menace known as the Joker wreaks havoc...", "year": 2008, "genre": "action", "img": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg"}
        ]
        filtered = [m for m in mock_movies if query in m['title'].lower()]
        return jsonify({"movies": filtered})
    
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
        
        movies_list.append({
            "id": int(row.get('id', idx)),
            "title": str(title),
            "overview": str(overview),
            "year": year,
            "genre": "drama",
            "img": poster_url
        })
    
    return jsonify({"movies": movies_list})

@app.route('/api/recommend/<int:movie_id>', methods=['GET'])
def recommend_movies(movie_id):
    """Get recommendations for a specific movie"""
    if knn_model is None or movies_df is None or X is None:
        return jsonify({"error": "Models not loaded"}), 500
    
    try:
        # Find movie index by ID
        movie_idx = None
        movie_row = None
        for idx, row in movies_df.iterrows():
            if int(row.get('id', idx)) == movie_id:
                movie_idx = idx
                movie_row = row
                break
        
        if movie_idx is None:
            return jsonify({"error": f"Movie with ID {movie_id} not found"}), 404
        
        print(f"Finding recommendations for: {movie_row['original_title']}")
        
        # Get recommendations
        distances, indices = knn_model.kneighbors([X[movie_idx]])
        recommended_indices = indices[0][1:]  # Exclude the movie itself
        
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
            
            # Calculate similarity score (convert distance to similarity percentage)
            distance = distances[0][i + 1]  # +1 because we excluded the original movie
            # Use exponential decay for better similarity scores
            similarity_score = float(np.exp(-distance / 10))  # Scale distance for better range
            
            # Get poster URL with fallback
            poster_url = get_poster_url(row, str(title))
            
            recommendations.append({
                "id": int(row.get('id', idx)),
                "title": str(title),
                "overview": str(overview),
                "year": year,
                "genre": "drama",
                "similarity_score": similarity_score,
                "img": poster_url
            })
        
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
            
            movies_list.append({
                "id": int(row.get('id', idx)),
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
        # Return mock recommendations
        return jsonify({
            "movie": {"id": 1, "title": "The Shawshank Redemption"},
            "recommendations": [
                {"id": 2, "title": "The Godfather", "overview": "The aging patriarch of an organized crime dynasty...", "year": 1972, "genre": "drama", "similarity_score": 0.85, "img": "https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsRolD1fZdja1.jpg"},
                {"id": 4, "title": "Pulp Fiction", "overview": "The lives of two mob hitmen, a boxer, a gangster...", "year": 1994, "genre": "drama", "similarity_score": 0.78, "img": "https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg"},
                {"id": 5, "title": "Forrest Gump", "overview": "The presidencies of Kennedy and Johnson...", "year": 1994, "genre": "drama", "similarity_score": 0.72, "img": "https://image.tmdb.org/t/p/w500/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg"}
            ]
        })
    
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
    app.run(debug=True, host='0.0.0.0', port=5000)