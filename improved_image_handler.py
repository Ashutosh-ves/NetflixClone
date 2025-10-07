import pandas as pd
import requests
import json
import time
from urllib.parse import quote
import re

class MovieImageHandler:
    """Enhanced movie image handler with multiple fallback strategies"""
    
    def __init__(self):
        # TMDB API configuration (you can get a free API key from themoviedb.org)
        self.tmdb_api_key = None  # Add your TMDB API key here if you have one
        self.tmdb_base_url = "https://image.tmdb.org/t/p/w500"
        
        # Alternative image services
        self.fallback_services = [
            "https://via.placeholder.com/300x450/1a1a2e/ffffff?text=",
            "https://dummyimage.com/300x450/1a1a2e/ffffff&text=",
            "https://picsum.photos/300/450?random="
        ]
        
        # Cache for processed images
        self.image_cache = {}
    
    def clean_title_for_url(self, title):
        """Clean movie title for use in URLs"""
        if not title or title == "Unknown Title":
            return "No+Title"
        
        # Remove special characters and limit length
        clean = re.sub(r'[^\w\s-]', '', str(title))
        clean = re.sub(r'\s+', '+', clean.strip())
        return clean[:30]  # Limit length for URL
    
    def get_tmdb_poster(self, poster_path):
        """Get TMDB poster URL if path exists"""
        if pd.notna(poster_path) and poster_path:
            # Clean the poster path
            if not poster_path.startswith('/'):
                poster_path = '/' + poster_path
            return f"{self.tmdb_base_url}{poster_path}"
        return None
    
    def get_placeholder_poster(self, title, year=None, service_index=0):
        """Generate placeholder poster with movie info"""
        clean_title = self.clean_title_for_url(title)
        
        if service_index == 0:  # via.placeholder.com
            year_text = f"+({year})" if year and year != 2000 else ""
            return f"https://via.placeholder.com/300x450/1a1a2e/ffffff?text={clean_title}{year_text}"
        
        elif service_index == 1:  # dummyimage.com
            year_text = f" ({year})" if year and year != 2000 else ""
            text = quote(f"{title[:20]}{year_text}")
            return f"https://dummyimage.com/300x450/1a1a2e/ffffff&text={text}"
        
        else:  # picsum.photos (random image)
            # Use title hash for consistent random image per movie
            hash_val = abs(hash(str(title))) % 1000
            return f"https://picsum.photos/300/450?random={hash_val}"
    
    def get_genre_based_poster(self, title, genres, year=None):
        """Generate genre-themed placeholder poster"""
        # Color schemes based on genres
        genre_colors = {
            'Action': ('8B0000', 'FFD700'),      # Dark red, gold
            'Adventure': ('228B22', 'FFFFFF'),    # Forest green, white
            'Animation': ('FF69B4', 'FFFFFF'),    # Hot pink, white
            'Comedy': ('FF8C00', 'FFFFFF'),       # Dark orange, white
            'Crime': ('2F4F4F', 'FF0000'),        # Dark slate gray, red
            'Drama': ('4B0082', 'FFFFFF'),        # Indigo, white
            'Family': ('32CD32', 'FFFFFF'),       # Lime green, white
            'Fantasy': ('9370DB', 'FFD700'),      # Medium purple, gold
            'Horror': ('000000', 'FF0000'),       # Black, red
            'Romance': ('DC143C', 'FFFFFF'),      # Crimson, white
            'Science Fiction': ('4169E1', 'FFFFFF'), # Royal blue, white
            'Thriller': ('8B0000', 'FFFFFF'),     # Dark red, white
            'War': ('556B2F', 'FFFFFF'),          # Dark olive green, white
            'Western': ('D2691E', 'FFFFFF'),      # Chocolate, white
        }
        
        # Find the first matching genre
        bg_color, text_color = '1a1a2e', 'ffffff'  # Default colors
        if genres:
            for genre in genres:
                if genre in genre_colors:
                    bg_color, text_color = genre_colors[genre]
                    break
        
        clean_title = self.clean_title_for_url(title)
        year_text = f"+({year})" if year and year != 2000 else ""
        
        return f"https://via.placeholder.com/300x450/{bg_color}/{text_color}?text={clean_title}{year_text}"
    
    def get_movie_poster(self, row, title, genres=None, year=None):
        """Get the best available poster for a movie with multiple fallbacks"""
        
        # Create cache key
        cache_key = f"{title}_{year}_{getattr(row, 'name', '')}"
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]
        
        poster_url = None
        
        # Strategy 1: Try TMDB poster path
        if hasattr(row, 'poster_path'):
            poster_url = self.get_tmdb_poster(row.poster_path)
        elif isinstance(row, dict) and 'poster_path' in row:
            poster_url = self.get_tmdb_poster(row['poster_path'])
        
        # Strategy 2: Try genre-based placeholder if we have genres
        if not poster_url and genres:
            poster_url = self.get_genre_based_poster(title, genres, year)
        
        # Strategy 3: Try regular placeholder
        if not poster_url:
            poster_url = self.get_placeholder_poster(title, year, 0)
        
        # Cache the result
        self.image_cache[cache_key] = poster_url
        return poster_url
    
    def validate_poster_url(self, url, timeout=5):
        """Validate if a poster URL is accessible (optional, can be slow)"""
        try:
            response = requests.head(url, timeout=timeout)
            return response.status_code == 200
        except:
            return False
    
    def get_poster_with_validation(self, row, title, genres=None, year=None, validate=False):
        """Get poster with optional URL validation"""
        poster_url = self.get_movie_poster(row, title, genres, year)
        
        if validate and poster_url:
            if not self.validate_poster_url(poster_url):
                # If validation fails, try next fallback
                poster_url = self.get_placeholder_poster(title, year, 1)
        
        return poster_url

# Test the image handler
def test_image_handler():
    """Test the image handler with sample data"""
    handler = MovieImageHandler()
    
    # Test cases
    test_movies = [
        {"title": "Toy Story", "genres": ["Animation", "Comedy", "Family"], "year": 1995, "poster_path": "/rhIRbceoE9lR4veEXuwCC2wARtG.jpg"},
        {"title": "The Dark Knight", "genres": ["Action", "Crime", "Drama"], "year": 2008, "poster_path": None},
        {"title": "Unknown Movie", "genres": ["Horror"], "year": 2020, "poster_path": None},
        {"title": "Test Film", "genres": [], "year": None, "poster_path": ""},
    ]
    
    print("🖼️  Testing Enhanced Image Handler")
    print("=" * 50)
    
    for movie in test_movies:
        print(f"\nMovie: {movie['title']} ({movie['year']})")
        print(f"Genres: {movie['genres']}")
        
        # Create a mock row object
        class MockRow:
            def __init__(self, data):
                for key, value in data.items():
                    setattr(self, key, value)
        
        row = MockRow(movie)
        poster_url = handler.get_movie_poster(row, movie['title'], movie['genres'], movie['year'])
        print(f"Poster URL: {poster_url}")

if __name__ == "__main__":
    test_image_handler()