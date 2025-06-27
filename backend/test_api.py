#!/usr/bin/env python3
"""
Test script for the Hylyte Backend API
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_health():
    """Test the health endpoint"""
    print("🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    print()

def test_highlight_video(youtube_url, user_prompt):
    """Test the highlight video endpoint"""
    print("🎬 Testing highlight video endpoint...")
    print(f"   URL: {youtube_url}")
    print(f"   Prompt: {user_prompt}")
    print()
    
    payload = {
        "youtube_url": youtube_url,
        "user_prompt": user_prompt
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/highlight-video",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Highlight video created successfully!")
            print(f"   Video Title: {data.get('video_title', 'N/A')}")
            print(f"   Highlights Found: {len(data.get('highlights', []))}")
            print(f"   Output Path: {data.get('highlight_video_path', 'N/A')}")
            
            # Show highlights
            highlights = data.get('highlights', [])
            if highlights:
                print("\n   📋 Highlights:")
                for i, highlight in enumerate(highlights, 1):
                    print(f"      {i}. {highlight['start_time']:.1f}s - {highlight['end_time']:.1f}s")
                    print(f"         {highlight['description']}")
                    print(f"         Relevance: {highlight['relevance_score']}/10")
        else:
            print("❌ Failed to create highlight video")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    print()

def main():
    print("🚀 Hylyte Backend API Test")
    print("=" * 50)
    
    # Test health endpoint
    test_health()
    
    # Test highlight video endpoint
    # You can change these values to test with different videos
    youtube_url = input("Enter YouTube URL (or press Enter for default): ").strip()
    if not youtube_url:
        youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    user_prompt = input("Enter your highlight prompt (or press Enter for default): ").strip()
    if not user_prompt:
        user_prompt = "Find the most exciting or memorable moments"
    
    test_highlight_video(youtube_url, user_prompt)
    
    print("🎉 Test completed!")

if __name__ == "__main__":
    main() 