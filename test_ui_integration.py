#!/usr/bin/env python3
"""
Test script to verify UI integration and complete workflow with different lecturers
"""

import requests
import time
import json

BASE_URL = "http://localhost:9000"

def test_ui_endpoints():
    """Test all the endpoints that the UI uses"""
    print("🔍 Testing UI Integration")
    print("=" * 50)
    
    # Test health endpoint
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health endpoint: {response.status_code} - {response.json()['status']}")
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
        return False
    
    # Test languages endpoint
    try:
        response = requests.get(f"{BASE_URL}/languages")
        languages = response.json()
        print(f"✅ Languages endpoint: {len(languages)} languages available")
        print(f"   Available languages: {', '.join(list(languages.keys())[:5])}...")
    except Exception as e:
        print(f"❌ Languages endpoint failed: {e}")
        return False
    
    # Test lecturers endpoint
    try:
        response = requests.get(f"{BASE_URL}/lecturers")
        lecturers_data = response.json()
        if isinstance(lecturers_data, dict) and 'lecturers' in lecturers_data:
            lecturers = lecturers_data['lecturers']
            print(f"✅ Lecturers endpoint: {len(lecturers)} lecturers available")
            for lecturer in lecturers[:3]:
                print(f"   - {lecturer['name']}")
        else:
            print(f"❌ Lecturers endpoint: Unexpected response format: {lecturers_data}")
            return False
    except Exception as e:
        print(f"❌ Lecturers endpoint failed: {e}")
        return False
    
    # Test tasks endpoint
    try:
        response = requests.get(f"{BASE_URL}/tasks")
        tasks = response.json()
        print(f"✅ Tasks endpoint: {len(tasks)} tasks")
    except Exception as e:
        print(f"❌ Tasks endpoint failed: {e}")
        return False
    
    return True

def test_video_generation():
    """Test video generation via API"""
    print("\n🎬 Testing Video Generation")
    print("=" * 50)
    # Use a known lecturer from the list
    test_data = {
        "text": "Hello! This is a test of the video generation system. The AI avatar is working correctly.",
        "language": "en",
        "lecturer_name": "Ankit Chauhan",
        "speed": "1.0"
    }
    try:
        form_data = {
            'text': test_data['text'],
            'language': test_data['language'],
            'lecturer_name': test_data['lecturer_name'],
            'speed': test_data['speed']
        }
        response = requests.post(f"{BASE_URL}/generate/text", data=form_data)
        if response.status_code == 200:
            result = response.json()
            task_id = result.get("task_id")
            print(f"✅ Video generation started: {task_id}")
            # Monitor task progress
            print("⏳ Monitoring task progress...")
            for i in range(60):  # Wait up to 60 seconds
                status_response = requests.get(f"{BASE_URL}/status/{task_id}")
                if status_response.status_code == 200:
                    status_info = status_response.json()
                    status = status_info.get("status")
                    print(f"   Status: {status}")
                    if status == "completed":
                        print(f"✅ Video generation completed!")
                        print(f"   Output: {status_info.get('result_url', 'N/A')}")
                        return True
                    elif status == "failed":
                        print(f"❌ Video generation failed: {status_info.get('error', 'Unknown error')}")
                        return False
                time.sleep(2)
            print("⚠️ Video generation timed out")
            return False
        else:
            print(f"❌ Video generation request failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Video generation test failed: {e}")
        return False

def test_gujarati_video_generation():
    """Test video generation for Gujarati lecturer in Gujarati language via API"""
    print("\n🎬 Testing Gujarati Video Generation")
    print("=" * 50)
    test_data = {
        "text": "આ એક ગુજરાતી ભાષામાં એઆઈ અવતાર સિસ્ટમનું પરીક્ષણ છે. આ સિસ્ટમ સફળતાપૂર્વક કાર્ય કરી રહી છે!",
        "language": "gu",
        "lecturer_name": "Gujarati",
        "speed": "1.0"
    }
    try:
        form_data = {
            'text': test_data['text'],
            'language': test_data['language'],
            'lecturer_name': test_data['lecturer_name'],
            'speed': test_data['speed']
        }
        response = requests.post(f"{BASE_URL}/generate/text", data=form_data)
        if response.status_code == 200:
            result = response.json()
            task_id = result.get("task_id")
            print(f"✅ Gujarati video generation started: {task_id}")
            # Monitor task progress
            print("⏳ Monitoring Gujarati task progress...")
            for i in range(60):  # Wait up to 60 seconds
                status_response = requests.get(f"{BASE_URL}/status/{task_id}")
                if status_response.status_code == 200:
                    status_info = status_response.json()
                    status = status_info.get("status")
                    print(f"   Status: {status}")
                    if status == "completed":
                        print(f"✅ Gujarati video generation completed!")
                        print(f"   Output: {status_info.get('result_url', 'N/A')}")
                        return True
                    elif status == "failed":
                        print(f"❌ Gujarati video generation failed: {status_info.get('error', 'Unknown error')}")
                        return False
                time.sleep(2)
            print("⚠️ Gujarati video generation timed out")
            return False
        else:
            print(f"❌ Gujarati video generation request failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Gujarati video generation test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting UI Integration Tests")
    print("=" * 60)
    # Test UI endpoints
    ui_test_passed = test_ui_endpoints()
    # Test video generation (English)
    video_test_passed = test_video_generation()
    # Test video generation (Gujarati)
    gujarati_test_passed = test_gujarati_video_generation()
    print("\n📊 Test Results Summary")
    print("=" * 40)
    print(f"UI Endpoints: {'✅ PASS' if ui_test_passed else '❌ FAIL'}")
    print(f"Video Generation (English): {'✅ PASS' if video_test_passed else '❌ FAIL'}")
    print(f"Video Generation (Gujarati): {'✅ PASS' if gujarati_test_passed else '❌ FAIL'}")
    if ui_test_passed and video_test_passed and gujarati_test_passed:
        print("\n🎉 All tests passed! UI integration is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the details above.")
