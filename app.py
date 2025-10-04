from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import joblib
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Load the trained models and data
try:
    knn_model = joblib.load('knn_model.joblib')
    tfidf_vectorizer = joblib.load('tfidf_vectorizer.joblib')
    movies_df = pd.read_csv('movies_preprocessed.csv', low_memory=False)
    
    # Preprocess the data (same as in model.py)
    movies_df['adult'] = movies_df['adult'].map({'True': 1, 'False': 0, True: 1, False: 0})
    text_data = movies_df['overview'].fillna('') + ' ' + movies_df['original_title'].fillna('')
    text_features = tfidf_vectorizer.transform(text_data).toarray()
    
    non_text_features = movies_df.drop(columns=['id', 'original_title', 'overview'])
    non_text_features = non_text_features.select_dtypes(include=[np.number])
    non_text_features = non_text_features.fillna(0)
    
    X = np.hstack([text_features, non_text_features.values])
    
    print("Models and data loaded successfully!")
    
except Exception as e:
    print(f"Error loading models: {e}")
    knn_model = None
    tfidf_vectorizer = None
    movies_df = None
    X = None

@app.route('/')
def home():
    return jsonify({"message": "Movie Recommendation API is running!"})

@app.route('/api/movies', methods=['GET'])
def get_movies():
    """Get all movies with basic info"""
    if movies_df is None:
        return jsonify({"error": "Models not loaded"}), 500
    
    # Return first 50 movies for frontend display
    movies_list = []
    for idx, row in movies_df.head(50).iterrows():
        movies_list.append({
            "id": int(row.get('id', idx)),
            "title": row['original_title'],
            "overview": row['overview'][:200] + "..." if len(str(row['overview'])) > 200 else row['overview'],
            "year": int(row.get('release_date', '2000')[:4]) if pd.notna(row.get('release_date')) else 2000,
            "genre": "drama"  # Default genre since we don't have genre data
        })
    
    return jsonify({"movies": movies_list})

@app.route('/api/search', methods=['GET'])
def search_movies():
    """Search movies by title"""
    query = request.args.get('q', '').lower()
    
    if movies_df is None:
        return jsonify({"error": "Models not loaded"}), 500
    
    if not query:
        return jsonify({"movies": []})
    
    # Filter movies by title
    filtered_movies = movies_df[movies_df['original_title'].str.lower().str.contains(query, na=False)]
    
    movies_list = []
    for idx, row in filtered_movies.head(20).iterrows():
        movies_list.append({
            "id": int(row.get('id', idx)),
            "title": row['original_title'],
            "overview": row['overview'][:200] + "..." if len(str(row['overview'])) > 200 else row['overview'],
            "year": int(row.get('release_date', '2000')[:4]) if pd.notna(row.get('release_date')) else 2000,
            "genre": "drama"
        })
    
    return jsonify({"movies": movies_list})

@app.route('/api/recommend/<int:movie_id>', methods=['GET'])
def recommend_movies(movie_id):
    """Get recommendations for a specific movie"""
    if knn_model is None or movies_df is None:
        return jsonify({"error": "Models not loaded"}), 500
    
    try:
        # Find movie index by ID
        movie_idx = None
        for idx, row in movies_df.iterrows():
            if int(row.get('id', idx)) == movie_id:
                movie_idx = idx
                break
        
        if movie_idx is None:
            return jsonify({"error": "Movie not found"}), 404
        
        # Get recommendations
        distances, indices = knn_model.kneighbors([X[movie_idx]])
        recommended_indices = indices[0][1:]  # Exclude the movie itself
        
        recommendations = []
        for idx in recommended_indices:
            row = movies_df.iloc[idx]
            recommendations.append({
                "id": int(row.get('id', idx)),
                "title": row['original_title'],
                "overview": row['overview'][:200] + "..." if len(str(row['overview'])) > 200 else row['overview'],
                "year": int(row.get('release_date', '2000')[:4]) if pd.notna(row.get('release_date')) else 2000,
                "genre": "drama",
                "similarity_score": float(1 / (1 + distances[0][list(indices[0]).index(idx)]))  # Convert distance to similarity
            })
        
        return jsonify({
            "movie": {
                "id": movie_id,
                "title": movies_df.iloc[movie_idx]['original_title']
            },
            "recommendations": recommendations
        })
        
    except Exception as e:
        return jsonify({"error": f"Recommendation failed: {str(e)}"}), 500

@app.route('/api/recommend/random', methods=['GET'])
def recommend_random():
    """Get recommendations for a random movie"""
    if movies_df is None:
        return jsonify({"error": "Models not loaded"}), 500
    
    # Pick a random movie
    random_idx = np.random.randint(0, len(movies_df))
    movie_id = int(movies_df.iloc[random_idx].get('id', random_idx))
    
    return recommend_movies(movie_id)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)