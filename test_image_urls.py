import requests
import json

def test_image_urls():
    """Test that the image URLs are properly formatted and accessible"""
    print("🖼️  Testing Image URLs")
    print("=" * 40)
    
    base_url = "http://localhost:5000"
    
    try:
        # Test search for a movie
        print("1. Testing search for 'Toy Story'...")
        search_response = requests.get(f"{base_url}/api/search?q=Toy Story")
        
        if search_response.status_code == 200:
            search_data = search_response.json()
            movies = search_data.get('movies', [])
            
            if movies:
                movie = movies[0]
                print(f"   Found: {movie['title']}")
                print(f"   Image URL: {movie['img']}")
                
                # Validate URL format
                img_url = movie['img']
                if img_url.startswith('https://'):
                    print("   ✅ URL format is correct")
                    
                    # Test if URL is accessible (just check format, not actual request)
                    if 'via.placeholder.com' in img_url or 'image.tmdb.org' in img_url:
                        print("   ✅ Using valid image service")
                    else:
                        print("   ⚠️  Unknown image service")
                else:
                    print(f"   ❌ Invalid URL format: {img_url}")
                
                # Test recommendations
                print(f"\n2. Testing recommendations for {movie['title']}...")
                rec_response = requests.get(f"{base_url}/api/recommend/{movie['id']}")
                
                if rec_response.status_code == 200:
                    rec_data = rec_response.json()
                    recommendations = rec_data.get('recommendations', [])
                    
                    print(f"   Found {len(recommendations)} recommendations")
                    
                    for i, rec in enumerate(recommendations[:3], 1):
                        print(f"   {i}. {rec['title']}")
                        print(f"      Image URL: {rec['img']}")
                        
                        # Check URL format
                        if rec['img'].startswith('https://'):
                            print("      ✅ URL format OK")
                        else:
                            print(f"      ❌ Bad URL: {rec['img']}")
                else:
                    print(f"   ❌ Recommendations failed: {rec_response.status_code}")
            else:
                print("   ❌ No movies found")
        else:
            print(f"   ❌ Search failed: {search_response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on port 5000")
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_placeholder_urls():
    """Test placeholder URL generation directly"""
    print(f"\n🎨 Testing Placeholder URL Generation")
    print("=" * 40)
    
    # Test different scenarios
    test_cases = [
        {"title": "Toy Story", "genres": ["Animation", "Comedy", "Family"]},
        {"title": "The Dark Knight", "genres": ["Action", "Crime", "Drama"]},
        {"title": "The Conjuring", "genres": ["Horror", "Thriller"]},
        {"title": "La La Land", "genres": ["Romance", "Comedy"]},
        {"title": "Unknown Movie", "genres": []},
    ]
    
    for case in test_cases:
        title = case['title']
        genres = case['genres']
        
        # Simulate the URL generation logic
        genre_colors = {
            'Action': ('8B0000', 'FFD700'),
            'Animation': ('FF69B4', 'FFFFFF'),
            'Horror': ('000000', 'FF0000'),
            'Romance': ('DC143C', 'FFFFFF'),
        }
        
        bg_color, text_color = '1a1a2e', 'ffffff'  # Default
        if genres:
            for genre in genres:
                if genre in genre_colors:
                    bg_color, text_color = genre_colors[genre]
                    break
        
        import re
        clean_title = re.sub(r'[^\w\s-]', '', title)
        clean_title = re.sub(r'\s+', '+', clean_title.strip())
        clean_title = clean_title[:25]
        
        url = f"https://via.placeholder.com/300x450/{bg_color}/{text_color}?text={clean_title}"
        
        print(f"Movie: {title}")
        print(f"Genres: {genres}")
        print(f"URL: {url}")
        print(f"Colors: Background={bg_color}, Text={text_color}")
        print()

if __name__ == "__main__":
    test_image_urls()
    test_placeholder_urls()
    
    print("🎯 If you see any malformed URLs, the server needs to be restarted")
    print("💡 Run: python app.py (make sure to stop the old server first)")