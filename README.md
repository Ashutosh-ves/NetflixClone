# CodeFlix - Movie Recommendation System

A Netflix-style movie recommendation system using KNN (K-Nearest Neighbors) machine learning model with a Flask backend and modern web frontend.

## Features

- 🎬 Movie recommendation system using KNN algorithm
- 🔍 Real-time movie search functionality
- 🎯 Personalized recommendations based on movie similarity
- 📱 Responsive Netflix-style UI
- 🚀 Flask REST API backend
- 🤖 Machine learning powered suggestions

## Project Structure

```
├── app.py                          # Flask backend server
├── model.py                        # KNN model training script
├── preproccessing.py              # Data preprocessing script
├── start_backend.py               # Backend startup script
├── requirements.txt               # Python dependencies
├── index.html                     # Frontend HTML
├── script.js                      # Frontend JavaScript
├── style.css                      # Frontend CSS
├── movies_metadata.csv            # Raw movie data
├── movies_preprocessed.csv        # Processed movie data
├── knn_model.joblib              # Trained KNN model
├── tfidf_vectorizer.joblib       # TF-IDF vectorizer
└── README.md                     # This file
```

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate Model Files (if not already done)

```bash
python model.py
```

This will create:
- `knn_model.joblib` - Trained KNN model
- `tfidf_vectorizer.joblib` - Text vectorizer
- `movies_preprocessed.csv` - Processed movie data

### 3. Start the Backend Server

Option A - Using the startup script:
```bash
python start_backend.py
```

Option B - Direct Flask run:
```bash
python app.py
```

The backend will be available at `http://localhost:5000`

### 4. Open the Frontend

Open `index.html` in your web browser or serve it using a local server:

```bash
# Using Python's built-in server
python -m http.server 8000

# Then open http://localhost:8000 in your browser
```

## API Endpoints

### GET /api/movies
Get a list of movies from the database.

**Response:**
```json
{
  "movies": [
    {
      "id": 1,
      "title": "Movie Title",
      "overview": "Movie description...",
      "year": 2023,
      "genre": "drama"
    }
  ]
}
```

### GET /api/search?q=<query>
Search for movies by title.

**Parameters:**
- `q` - Search query string

**Response:**
```json
{
  "movies": [...]
}
```

### GET /api/recommend/<movie_id>
Get recommendations for a specific movie.

**Response:**
```json
{
  "movie": {
    "id": 1,
    "title": "Selected Movie"
  },
  "recommendations": [
    {
      "id": 2,
      "title": "Recommended Movie",
      "overview": "Description...",
      "year": 2023,
      "genre": "drama",
      "similarity_score": 0.85
    }
  ]
}
```

### GET /api/recommend/random
Get recommendations for a randomly selected movie.

## How It Works

1. **Data Processing**: Movie metadata is preprocessed to extract features
2. **Feature Engineering**: TF-IDF vectorization for text data + numerical features
3. **Model Training**: KNN algorithm finds similar movies in feature space
4. **API Layer**: Flask serves the model through REST endpoints
5. **Frontend**: Interactive web interface for browsing and getting recommendations

## Machine Learning Details

- **Algorithm**: K-Nearest Neighbors (KNN)
- **Features**: 
  - TF-IDF vectors from movie titles and overviews
  - Numerical movie metadata (ratings, year, etc.)
- **Similarity Metric**: Euclidean distance
- **Neighbors**: 6 (returns 5 recommendations + original movie)

## Frontend Features

- **Netflix-style UI**: Modern, responsive design
- **Movie Cards**: Click any movie to get recommendations
- **Search Functionality**: Real-time search with backend integration
- **Recommendation Modal**: Displays similar movies with similarity scores
- **Responsive Design**: Works on desktop and mobile devices

## Troubleshooting

### Backend Issues

1. **Model files missing**: Run `python model.py` to generate them
2. **Port already in use**: Change the port in `app.py` (line with `app.run()`)
3. **CORS errors**: Make sure Flask-CORS is installed and configured

### Frontend Issues

1. **API connection failed**: Ensure backend is running on `http://localhost:5000`
2. **Images not loading**: Check internet connection for movie poster URLs
3. **Search not working**: Verify backend API endpoints are accessible

## Development

To modify the recommendation algorithm:
1. Edit `model.py` to change features or algorithm
2. Retrain the model: `python model.py`
3. Restart the backend: `python app.py`

To modify the frontend:
1. Edit `script.js` for functionality changes
2. Edit `style.css` for styling changes
3. Edit `index.html` for structure changes

## License

This project is for educational purposes. Movie data and images are used for demonstration only.