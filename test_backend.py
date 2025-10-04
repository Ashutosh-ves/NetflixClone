#!/usr/bin/env python3
"""
Test script to verify the backend functionality
"""

import requests
import json
import time
import subprocess
import sys
from threading import Thread

def test_api_endpoints():
    """Test all API endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing API Endpoints")
    print("-" * 30)
    
    # Test home endpoint
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Home endpoint working")
        else:
            print(f"❌ Home endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Home endpoint error: {e}")
        return False
    
    # Test movies endpoint
    try:
        response = requests.get(f"{base_url}/api/movies")
        if response.status_code == 200:
            data = response.json()
            movie_count = len(data.get('movies', []))
            print(f"✅ Movies endpoint working - {movie_count} movies loaded")
        else:
            print(f"❌ Movies endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Movies endpoint error: {e}")
    
    # Test search endpoint
    try:
        response = requests.get(f"{base_url}/api/search?q=the")
        if response.status_code == 200:
            data = response.json()
            search_count = len(data.get('movies', []))
            print(f"✅ Search endpoint working - {search_count} results for 'the'")
        else:
            print(f"❌ Search endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Search endpoint error: {e}")
    
    # Test random recommendations
    try:
        response = requests.get(f"{base_url}/api/recommend/random")
        if response.status_code == 200:
            data = response.json()
            rec_count = len(data.get('recommendations', []))
            movie_title = data.get('movie', {}).get('title', 'Unknown')
            print(f"✅ Random recommendations working - {rec_count} recommendations for '{movie_title}'")
        else:
            print(f"❌ Random recommendations failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Random recommendations error: {e}")
    
    print("\n🎉 Backend testing completed!")
    return True

if __name__ == "__main__":
    print("🎬 CodeFlix Backend Test")
    print("=" * 30)
    
    print("Make sure the backend is running on http://localhost:5000")
    print("You can start it with: python app.py")
    print("\nPress Enter to start testing...")
    input()
    
    test_api_endpoints()