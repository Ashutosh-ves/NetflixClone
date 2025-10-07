import requests
import json

# Test the movie details API endpoint
base_url = "http://localhost:5000"

def test_movie_details():
    print("🎬 Testing Movie Details API")
    print("=" * 40)
    
    # First, search for a movie to get its ID
    print("1. Searching for 'Toy Story'...")
    search_response = requests.get(f"{base_url}/api/search?q=Toy Story")
    
    if search_response.status_code == 200:
        search_data = search_response.json()
        movies = search_data.get('movies', [])
        
        if movies:
            toy_story = movies[0]
            print(f"   Found: {toy_story['title']} (ID: {toy_story['id']})")
            
            # Test movie details endpoint
            print(f"\n2. Getting details for movie ID {toy_story['id']}...")
            details_response = requests.get(f"{base_url}/api/movie/{toy_story['id']}")
            
            if details_response.status_code == 200:
                details_data = details_response.json()
                movie = details_data.get('movie', {})
                
                print(f"✅ Movie Details Retrieved:")
                print(f"   Title: {movie.get('title', 'N/A')}")
                print(f"   Year: {movie.get('year', 'N/A')}")
                print(f"   Genres: {', '.join(movie.get('genres', []))}")
                print(f"   Overview: {movie.get('overview', 'N/A')[:100]}...")
                print(f"   Has Poster: {'Yes' if movie.get('img') else 'No'}")
                
                # Test recommendations for this movie
                print(f"\n3. Getting recommendations for {movie.get('title')}...")
                rec_response = requests.get(f"{base_url}/api/recommend/{toy_story['id']}")
                
                if rec_response.status_code == 200:
                    rec_data = rec_response.json()
                    recommendations = rec_data.get('recommendations', [])
                    
                    print(f"✅ Found {len(recommendations)} recommendations:")
                    for i, rec in enumerate(recommendations[:3], 1):
                        print(f"   {i}. {rec['title']} (Similarity: {rec['similarity_score']:.3f})")
                    
                    # Test details for a recommended movie
                    if recommendations:
                        rec_movie = recommendations[0]
                        print(f"\n4. Testing details for recommended movie: {rec_movie['title']}")
                        rec_details_response = requests.get(f"{base_url}/api/movie/{rec_movie['id']}")
                        
                        if rec_details_response.status_code == 200:
                            print("✅ Recommended movie details working!")
                        else:
                            print(f"❌ Failed to get recommended movie details: {rec_details_response.status_code}")
                else:
                    print(f"❌ Failed to get recommendations: {rec_response.status_code}")
            else:
                print(f"❌ Failed to get movie details: {details_response.status_code}")
        else:
            print("❌ No movies found in search")
    else:
        print(f"❌ Search failed: {search_response.status_code}")

if __name__ == "__main__":
    try:
        test_movie_details()
        print("\n🎉 Movie details testing complete!")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure it's running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Test failed: {e}")