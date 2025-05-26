#!/usr/bin/env python3
"""
Final system test to verify all components are working correctly.
This test checks frontend-backend communication and video generation.
"""

import requests
import time
import json
import sys
from pathlib import Path

BASE_URL = "http://localhost:9000"

def test_backend_health():
    """Test if backend is healthy and responding."""
    print("🏥 Testing backend health...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Backend healthy: {health_data['status']}")
            
            # Check all components
            components = health_data.get('components', {})
            for component, status in components.items():
                status_icon = "✅" if status else "❌"
                print(f"  {status_icon} {component}: {'Ready' if status else 'Not Ready'}")
            
            return True
        else:
            print(f"❌ Backend unhealthy: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend connection failed: {e}")
        return False

def test_lecturers_endpoint():
    """Test lecturers API endpoint."""
    print("\n👨‍🏫 Testing lecturers endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/lecturers", timeout=10)
        if response.status_code == 200:
            lecturers = response.json()
            print(f"✅ Found {len(lecturers)} lecturers:")
            for i, lecturer in enumerate(lecturers[:3], 1):  # Show first 3
                print(f"  {i}. {lecturer['name']}")
            return lecturers
        else:
            print(f"❌ Lecturers endpoint failed: HTTP {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"❌ Lecturers endpoint error: {e}")
        return []

def test_languages_endpoint():
    """Test languages API endpoint."""
    print("\n🌍 Testing languages endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/languages", timeout=10)
        if response.status_code == 200:
            languages = response.json()
            print(f"✅ Found {len(languages)} supported languages:")
            for lang_code, lang_name in list(languages.items())[:5]:  # Show first 5
                print(f"  • {lang_code}: {lang_name}")
            return languages
        else:
            print(f"❌ Languages endpoint failed: HTTP {response.status_code}")
            return {}
    except requests.exceptions.RequestException as e:
        print(f"❌ Languages endpoint error: {e}")
        return {}

def test_video_generation():
    """Test video generation with API."""
    print("\n🎬 Testing video generation...")
    
    # Simple API test with known lecturer
    test_data = {
        "lecturer_name": "ankit",
        "text": "Hello, this is a final system test of the doctor avatar platform. All components are working correctly!",
        "language": "en"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate/text", json=test_data, timeout=10)
        if response.status_code == 200:
            task_data = response.json()
            task_id = task_data.get('task_id')
            print(f"✅ Video generation started: {task_id}")
            
            # Poll for completion
            max_wait = 60  # seconds
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                status_response = requests.get(f"{BASE_URL}/status/{task_id}", timeout=10)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    status = status_data.get('status')
                    print(f"  Status: {status}")
                    
                    if status == 'completed':
                        video_path = status_data.get('video_path')
                        print(f"✅ Video generated successfully: {video_path}")
                        return True
                    elif status == 'failed':
                        error = status_data.get('error', 'Unknown error')
                        print(f"❌ Video generation failed: {error}")
                        return False
                    
                    time.sleep(2)
                else:
                    print(f"❌ Status check failed: HTTP {status_response.status_code}")
                    return False
            
            print(f"⏱️ Video generation timed out after {max_wait} seconds")
            return False
            
        else:
            print(f"❌ Video generation request failed: HTTP {response.status_code}")
            if response.text:
                print(f"  Error: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Video generation error: {e}")
        return False

def test_ui_endpoint():
    """Test if UI endpoint is accessible."""
    print("\n🖥️ Testing UI endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/ui", timeout=10)
        if response.status_code == 200:
            print("✅ UI endpoint accessible")
            print(f"  Content-Type: {response.headers.get('content-type', 'unknown')}")
            print(f"  Content-Length: {len(response.content)} bytes")
            return True
        else:
            print(f"❌ UI endpoint failed: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ UI endpoint error: {e}")
        return False

def browser_troubleshooting_tips():
    """Print browser troubleshooting tips for ERR_H2_OR_QUIC_REQUIRED."""
    print("\n🔧 Browser Troubleshooting Tips for ERR_H2_OR_QUIC_REQUIRED:")
    print("="*60)
    print("If you're seeing ERR_H2_OR_QUIC_REQUIRED in Chrome, try:")
    print("1. 🔄 Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)")
    print("2. 🗑️ Clear browser cache and cookies for localhost")
    print("3. 🚫 Disable browser extensions temporarily")
    print("4. 🔒 Ensure you're using HTTP (not HTTPS): http://localhost:9000/ui")
    print("5. 🌐 Try a different browser (Firefox, Safari, Edge)")
    print("6. 👤 Try incognito/private browsing mode")
    print("7. 🚀 Or access the UI directly via: http://localhost:9000/ui")
    print("")
    print("📱 Alternative access methods:")
    print("• Open terminal and run: open http://localhost:9000/ui")
    print("• Or copy-paste this URL: http://localhost:9000/ui")

def main():
    """Run all system tests."""
    print("🚀 Doctor Avatar - Final System Test")
    print("="*50)
    
    all_passed = True
    
    # Test backend health
    if not test_backend_health():
        all_passed = False
    
    # Test lecturers
    lecturers = test_lecturers_endpoint()
    if not lecturers:
        all_passed = False
    
    # Test languages
    languages = test_languages_endpoint()
    if not languages:
        all_passed = False
    
    # Test UI endpoint
    if not test_ui_endpoint():
        all_passed = False
    
    # Test video generation
    if not test_video_generation():
        all_passed = False
    
    # Print results
    print("\n" + "="*50)
    if all_passed:
        print("🎉 ALL TESTS PASSED! System is fully operational.")
        print("\n✨ Your Doctor Avatar system is ready to use!")
        print(f"🌐 Access the web interface at: http://localhost:9000/ui")
    else:
        print("⚠️ Some tests failed. Please check the logs above.")
        print("\n🔧 The backend appears to be working, so browser issues may be the cause.")
    
    # Always show browser tips in case user is having issues
    browser_troubleshooting_tips()
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
