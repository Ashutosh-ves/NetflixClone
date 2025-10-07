import requests
import json

# Test the improved recommendation API
base_url = "http://localhost:5000"

def test_search_and_recommend():
    print("🎬 Testing Improved Movie Recommendation System")
    print("=" * 50)
    
    # Search for Toy Story
    print("1. Searching for 'Toy Story'...")
    search_response = requests.get(f"{base_url}/api/search?q=Toy Story")
    
    if search_response.status_code == 200:
        search_data = search_response.json()
        movies = search_data.get('movies', [])
        
        if movies:
            toy_story = movies[0]  # Get first Toy Story result
            print(f"   Found: {toy_story['title']} (ID: {toy_story['id']})")
            
            # Get recommendations
            print(f"\n2. Getting recommendations for '{toy_story['title']}'...")
            rec_response = requests.get(f"{base_url}/api/recommend/{toy_story['id']}")
            
            if rec_response.status_code == 200:
                rec_data = rec_response.json()
                recommendations = rec_data.get('recommendations', [])
                
                print(f"\n✅ Improved Recommendations for {toy_story['title']}:")
                print("-" * 40)
                
                for i, rec in enumerate(recommendations, 1):
                    print(f"{i}. {rec['title']} ({rec['year']})")
                    print(f"   Similarity: {rec['similarity_score']:.3f}")
                    print(f"   Overview: {rec['overview'][:100]}...")
                    print()
                
                # Check if recommendations are better (should be animated/family films)
                animated_count = sum(1 for rec in recommendations if 'animation' in rec['overview'].lower() or 'animated' in rec['overview'].lower())
                family_count = sum(1 for rec in recommendations if 'family' in rec['overview'].lower() or 'children' in rec['overview'].lower())
                
                print(f"📊 Quality Check:")
                print(f"   - Animated/Family-related recommendations: {animated_count + family_count}/5")
                print(f"   - Average similarity score: {sum(rec['similarity_score'] for rec in recommendations)/len(recommendations):.3f}")
                
            else:
                print(f"❌ Failed to get recommendations: {rec_response.status_code}")
        else:
            print("❌ No Toy Story movies found")
    else:
        print(f"❌ Search failed: {search_response.status_code}")

def test_random_recommendations():
    print("\n" + "=" * 50)
    print("3. Testing random recommendations...")
    
    response = requests.get(f"{base_url}/api/recommend/random")
    if response.status_code == 200:
        data = response.json()
        movie = data.get('movie', {})
        recommendations = data.get('recommendations', [])
        
        print(f"Random movie: {movie.get('title', 'Unknown')}")
        print(f"Recommendations: {len(recommendations)} movies")
        print("✅ Random recommendations working!")
    else:
        print(f"❌ Random recommendations failed: {response.status_code}")

if __name__ == "__main__":
    try:
        test_search_and_recommend()
        test_random_recommendations()
        print("\n🎉 Testing complete!")
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure it's running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Test failed: {e}")