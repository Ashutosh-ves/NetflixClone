import pandas as pd
import numpy as np

def analyze_movie_images():
    """Analyze the current state of movie images in the dataset"""
    print("🖼️  MOVIE IMAGE ANALYSIS")
    print("=" * 50)
    
    try:
        # Load the data
        print("Loading movie data...")
        movies_df = pd.read_csv('movies_preprocessed.csv', low_memory=False)
        original_df = pd.read_csv('movies_metadata.csv', low_memory=False)
        
        # Merge poster paths
        movies_df = movies_df.merge(original_df[['id', 'poster_path', 'release_date']], on='id', how='left', suffixes=('', '_orig'))
        
        total_movies = len(movies_df)
        print(f"Total movies in dataset: {total_movies:,}")
        
        # Analyze poster availability
        movies_with_posters = movies_df['poster_path'].notna().sum()
        movies_without_posters = total_movies - movies_with_posters
        poster_coverage = (movies_with_posters / total_movies) * 100
        
        print(f"\n📊 POSTER AVAILABILITY:")
        print(f"  Movies with TMDB posters: {movies_with_posters:,} ({poster_coverage:.1f}%)")
        print(f"  Movies without posters: {movies_without_posters:,} ({100-poster_coverage:.1f}%)")
        
        # Analyze by genre
        genre_columns = ['Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Documentary', 
                        'Drama', 'Family', 'Fantasy', 'Horror', 'Music', 'Mystery', 
                        'Romance', 'Science Fiction', 'Thriller', 'War', 'Western']
        
        available_genres = [col for col in genre_columns if col in movies_df.columns]
        
        print(f"\n🎭 POSTER AVAILABILITY BY GENRE:")
        for genre in available_genres:
            genre_movies = movies_df[movies_df[genre] == 1]
            if len(genre_movies) > 0:
                genre_with_posters = genre_movies['poster_path'].notna().sum()
                genre_coverage = (genre_with_posters / len(genre_movies)) * 100
                print(f"  {genre:15}: {genre_with_posters:4}/{len(genre_movies):4} ({genre_coverage:5.1f}%)")
        
        # Sample movies without posters
        print(f"\n🔍 SAMPLE MOVIES WITHOUT POSTERS:")
        no_poster_movies = movies_df[movies_df['poster_path'].isna()].head(10)
        for idx, row in no_poster_movies.iterrows():
            title = row['original_title'] if pd.notna(row['original_title']) else "Unknown Title"
            year = "N/A"
            if pd.notna(row.get('release_date')):
                try:
                    year = str(row['release_date'])[:4]
                except:
                    pass
            
            # Get genres for this movie
            movie_genres = [genre for genre in available_genres if row[genre] == 1]
            genres_str = ", ".join(movie_genres) if movie_genres else "No genres"
            
            print(f"  • {title} ({year}) - {genres_str}")
        
        # Recommendations for improvement
        print(f"\n💡 IMPROVEMENT STRATEGIES:")
        print(f"  1. ✅ Genre-based colored placeholders (implemented)")
        print(f"  2. ✅ Title-based placeholder generation (implemented)")
        print(f"  3. ✅ Multiple fallback services (implemented)")
        print(f"  4. 🔄 TMDB API integration (optional - requires API key)")
        print(f"  5. 🔄 Web scraping for additional posters (advanced)")
        print(f"  6. 🔄 AI-generated posters (advanced)")
        
        # Show improvement impact
        print(f"\n📈 EXPECTED IMPROVEMENT:")
        print(f"  Current coverage: {poster_coverage:.1f}%")
        print(f"  With enhanced placeholders: 100% (all movies will have visual representation)")
        print(f"  Visual quality: Significantly improved with genre-based colors")
        
    except FileNotFoundError as e:
        print(f"❌ Error: Could not find required files")
        print(f"   Make sure you have: movies_preprocessed.csv and movies_metadata.csv")
    except Exception as e:
        print(f"❌ Error analyzing images: {e}")

def show_enhanced_examples():
    """Show examples of enhanced image URLs"""
    from improved_image_handler import MovieImageHandler
    
    print(f"\n🎨 ENHANCED IMAGE EXAMPLES:")
    print("=" * 50)
    
    handler = MovieImageHandler()
    
    # Example movies with different scenarios
    examples = [
        {"title": "Toy Story", "genres": ["Animation", "Comedy", "Family"], "year": 1995, "has_poster": True},
        {"title": "The Shawshank Redemption", "genres": ["Drama"], "year": 1994, "has_poster": False},
        {"title": "Mad Max: Fury Road", "genres": ["Action", "Adventure"], "year": 2015, "has_poster": False},
        {"title": "The Conjuring", "genres": ["Horror", "Thriller"], "year": 2013, "has_poster": False},
        {"title": "La La Land", "genres": ["Romance", "Comedy"], "year": 2016, "has_poster": False},
    ]
    
    for example in examples:
        print(f"\n🎬 {example['title']} ({example['year']})")
        print(f"   Genres: {', '.join(example['genres'])}")
        print(f"   Has TMDB poster: {'Yes' if example['has_poster'] else 'No'}")
        
        # Create mock row
        class MockRow:
            def __init__(self, has_poster):
                self.poster_path = "/sample.jpg" if has_poster else None
        
        row = MockRow(example['has_poster'])
        enhanced_url = handler.get_movie_poster(row, example['title'], example['genres'], example['year'])
        print(f"   Enhanced URL: {enhanced_url}")

if __name__ == "__main__":
    analyze_movie_images()
    show_enhanced_examples()
    
    print(f"\n🚀 NEXT STEPS:")
    print(f"  1. Run: python app_with_better_images.py")
    print(f"  2. Test the enhanced image system on port 5003")
    print(f"  3. Compare with original system to see the improvement")