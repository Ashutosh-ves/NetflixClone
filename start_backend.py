#!/usr/bin/env python3
"""
Simple script to start the Flask backend server
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False
    return True

def check_model_files():
    """Check if model files exist"""
    required_files = [
        'knn_model.joblib',
        'tfidf_vectorizer.joblib',
        'movies_preprocessed.csv'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        print("Please run model.py first to generate the model files.")
        return False
    
    print("✅ All required model files found!")
    return True

def start_server():
    """Start the Flask server"""
    print("Starting Flask backend server...")
    print("Server will be available at: http://localhost:5000")
    print("API endpoints:")
    print("  - GET /api/movies - Get all movies")
    print("  - GET /api/search?q=<query> - Search movies")
    print("  - GET /api/recommend/<movie_id> - Get recommendations")
    print("  - GET /api/recommend/random - Get random recommendations")
    print("\nPress Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n✅ Server stopped successfully!")

if __name__ == "__main__":
    print("🎬 CodeFlix Backend Startup")
    print("=" * 30)
    
    # Check if model files exist
    if not check_model_files():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Start server
    start_server()