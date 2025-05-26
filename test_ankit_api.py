#!/usr/bin/env python3
"""
Simple test script to generate a video using Ankit's files via the web API.
"""

import requests
import json
import time
import os
from pathlib import Path

def test_web_api():
    """Test the web API with Ankit's files."""
    
    base_url = "http://localhost:9000"
    
    # First, check if the server is responding
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Server health check: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Server not responding: {e}")
        return False
    
    # Check existing lecturers
    try:
        response = requests.get(f"{base_url}/lecturers")
        print(f"✅ Lecturers endpoint: {response.status_code}")
        if response.status_code == 200:
            lecturers = response.json()
            print(f"   Available lecturers: {lecturers}")
            lecturer_names = [lecturer["name"] for lecturer in lecturers["lecturers"]]
            if "Ankit Chauhan" in lecturer_names:
                print("   ✅ Ankit Chauhan is available as a lecturer!")
            else:
                print("   ⚠️ Ankit Chauhan not found in lecturers list")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error getting lecturers: {e}")
    
    # Test video generation with text
    print("\n🎬 Testing video generation with text...")
    try:
        data = {
            "text": "Hello, this is Ankit Chauhan testing the avatar system. The doctor avatar technology is working perfectly with my custom portrait and voice.",
            "language": "en",
            "lecturer_name": "Ankit Chauhan",
            "speed": "1.0"
        }
        
        print(f"   Sending form data: {data}")
        response = requests.post(f"{base_url}/generate/text", data=data, timeout=300)
        print(f"   Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Video generation successful!")
            print(f"   📁 Video path: {result.get('video_path', 'N/A')}")
            print(f"   📊 Success: {result.get('success', False)}")
            if 'audio_path' in result:
                print(f"   🔊 Audio path: {result['audio_path']}")
        else:
            print(f"   ❌ Video generation failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error in video generation: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Ankit's video generation test via Web API...")
    print("="*60)
    
    success = test_web_api()
    
    if success:
        print("\n🎉 Test completed!")
    else:
        print("\n❌ Test failed!")
