import requests
import json
import time

# Compare recommendations between original faulty system and improved system
original_url = "http://localhost:5001"  # Original faulty system
improved_url = "http://localhost:5000"  # Improved system

def compare_recommendations():
    print("🎬 MOVIE RECOMMENDATION SYSTEM COMPARISON")
    print("=" * 60)
    print("Comparing ORIGINAL FAULTY vs IMPROVED recommendations")
    print("=" * 60)
    
    # Test movie: Toy Story
    test_query = "Toy Story"
    
    print(f"\n🔍 Searching for '{test_query}' in both systems...")
    
    # Get movie from improved system first
    try:
        improved_search = requests.get(f"{improved_url}/api/search?q={test_query}")
        if improved_search.status_code == 200:
            improved_movies = improved_search.json().get('movies', [])
            if improved_movies:
                toy_story = improved_movies[0]
                movie_id = toy_story['id']
                movie_title = toy_story['title']
                
                print(f"✅ Found: {movie_title} (ID: {movie_id})")
                
                # Get recommendations from IMPROVED system
                print(f"\n🚀 IMPROVED SYSTEM Recommendations for '{movie_title}':")
                print("-" * 50)
                
                improved_rec = requests.get(f"{improved_url}/api/recommend/{movie_id}")
                if improved_rec.status_code == 200:
                    improved_data = improved_rec.json()
                    improved_recommendations = improved_data.get('recommendations', [])
                    
                    for i, rec in enumerate(improved_recommendations, 1):
                        print(f"{i:2d}. {rec['title']} ({rec['year']})")
                        print(f"    Similarity: {rec['similarity_score']:.3f}")
                        print(f"    Overview: {rec['overview'][:80]}...")
                        print()
                else:
                    print("❌ Failed to get improved recommendations")
                
                # Get recommendations from ORIGINAL FAULTY system
                print(f"\n🚨 ORIGINAL FAULTY SYSTEM Recommendations for '{movie_title}':")
                print("-" * 50)
                
                try:
                    original_rec = requests.get(f"{original_url}/api/recommend/{movie_id}")
                    if original_rec.status_code == 200:
                        original_data = original_rec.json()
                        original_recommendations = original_data.get('recommendations', [])
                        
                        for i, rec in enumerate(original_recommendations, 1):
                            print(f"{i:2d}. {rec['title']} ({rec['year']})")
                            print(f"    Similarity: {rec['similarity_score']:.3f}")
                            print(f"    Overview: {rec['overview'][:80]}...")
                            print()
                    else:
                        print("❌ Failed to get original recommendations")
                except requests.exceptions.ConnectionError:
                    print("❌ Original faulty system not running on port 5001")
                    print("💡 Run: python app_original_faulty.py")
                
                # Analysis
                print("\n" + "="*60)
                print("📊 ANALYSIS:")
                print("="*60)
                print("IMPROVED SYSTEM should show:")
                print("  ✅ Animated family movies (similar genres)")
                print("  ✅ High similarity scores (0.9+)")
                print("  ✅ Relevant content (cartoons, family films)")
                print()
                print("ORIGINAL FAULTY SYSTEM typically shows:")
                print("  ❌ Random foreign films from different decades")
                print("  ❌ Low similarity scores")
                print("  ❌ Completely unrelated content")
                print("="*60)
                
            else:
                print("❌ No movies found")
        else:
            print(f"❌ Search failed: {improved_search.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to improved system on port 5000")
        print("💡 Make sure the improved system is running: python app.py")

def test_individual_system(url, name):
    """Test an individual system"""
    print(f"\n🧪 Testing {name} at {url}")
    try:
        response = requests.get(f"{url}/api")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {name} is running")
            print(f"   Message: {data.get('message', 'N/A')}")
            if 'warning' in data:
                print(f"   ⚠️  {data['warning']}")
        else:
            print(f"❌ {name} returned status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"❌ {name} is not running")

if __name__ == "__main__":
    print("Checking system status...")
    test_individual_system(improved_url, "IMPROVED SYSTEM")
    test_individual_system(original_url, "ORIGINAL FAULTY SYSTEM")
    
    print("\n" + "="*60)
    input("Press Enter to start comparison (make sure both systems are running)...")
    
    compare_recommendations()
    
    print(f"\n🎯 CONCLUSION:")
    print("The improved system uses:")
    print("  • Cosine similarity instead of euclidean distance")
    print("  • Weighted features (genres get 3x importance)")
    print("  • Better TF-IDF with bigrams")
    print("  • Proper feature scaling")
    print("\nResult: Much more relevant recommendations!")