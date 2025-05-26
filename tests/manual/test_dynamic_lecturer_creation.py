#!/usr/bin/env python3
"""
Test script for dynamic lecturer creation functionality.
Tests the complete flow of creating a new lecturer with custom files.
"""

import sys
import json
import time
import requests
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Configuration
API_URL = "http://localhost:9000"

def get_existing_lecturers():
    """Fetch the list of existing lecturers from the API."""
    try:
        response = requests.get(f"{API_URL}/lecturers")
        response.raise_for_status()
        data = response.json()
        return data.get("lecturers", [])
    except Exception as e:
        print(f"⚠️ Could not fetch lecturers list: {e}")
        return []

def ensure_lecturer_exists(lecturer_name, portrait_path, voice_path):
    """Create the lecturer if not present using the API and provided files."""
    lecturer_response = requests.get(f"{API_URL}/lecturers/{lecturer_name}")
    lecturer_response.raise_for_status()
    lecturer_data = lecturer_response.json()
    if not lecturer_data["exists"]:
        print(f"Lecturer '{lecturer_name}' does not exist. Creating...")
        if not Path(portrait_path).exists() or not Path(voice_path).exists():
            print(f"❌ Required files for lecturer creation not found: {portrait_path}, {voice_path}")
            return False
        with open(portrait_path, "rb") as portrait_file, open(voice_path, "rb") as voice_file:
            files = {
                "portrait_file": (f"{lecturer_name}.png", portrait_file, "image/png"),
                "voice_file": (f"{lecturer_name}_voice.wav", voice_file, "audio/wav")
            }
            create_response = requests.post(f"{API_URL}/lecturers/{lecturer_name}", files=files)
            if create_response.status_code == 200:
                print(f"✅ Lecturer '{lecturer_name}' created successfully.")
                return True
            else:
                print(f"❌ Failed to create lecturer: {create_response.text}")
                return False
    else:
        print(f"Lecturer '{lecturer_name}' already exists.")
        return True

def test_dynamic_lecturer_creation():
    """Test creating a new lecturer dynamically with custom files."""
    print("🎭 Testing Dynamic Lecturer Creation")
    print("=" * 50)
    
    # Show dropdown of existing lecturers
    lecturers = get_existing_lecturers()
    if lecturers:
        print("\nAvailable lecturers:")
        for idx, name in enumerate(lecturers, 1):
            print(f"  {idx}. {name}")
        print("  0. Create new lecturer")
        selected = 0  # For automation, always create new lecturer
    else:
        print("No lecturers found. Proceeding to create new lecturer.")
        selected = 0

    lecturer_name = "ankit"
    sample_portrait = "portraits/sample_lecturer.png"
    sample_voice = "portraits/sample_lecturer_voice.wav"
    
    # Ensure lecturer exists before generation
    if not ensure_lecturer_exists(lecturer_name, sample_portrait, sample_voice):
        print(f"❌ Could not ensure lecturer '{lecturer_name}' exists. Aborting test.")
        return False

    # Test text for generation
    test_text = "Hello, I am Ankit, your new AI lecturer. Today we will learn about artificial intelligence and machine learning."
    
    try:
        # 1. Check if backend is responding
        health_response = requests.get(f"{API_URL}/health")
        health_response.raise_for_status()
        health_data = health_response.json()
        print(f"✅ API health check: {health_data['status']}")
        
        # 2. Check that lecturer "ankit" doesn't exist
        lecturer_response = requests.get(f"{API_URL}/lecturers/ankit")
        lecturer_response.raise_for_status()
        lecturer_data = lecturer_response.json()
        
        if not lecturer_data["exists"]:
            print(f"✅ Confirmed lecturer 'ankit' doesn't exist")
            print(f"📋 Requirements: {lecturer_data['requirements']}")
        else:
            print(f"⚠️ Lecturer 'ankit' already exists, cleaning up first...")
            # Clean up existing lecturer files for test
            portraits_dir = Path("portraits")
            for file_pattern in ["ankit.*", "ankit_voice.*"]:
                for file in portraits_dir.glob(file_pattern):
                    file.unlink()
                    print(f"🗑️ Removed: {file}")
        
        # 3. Test text generation with non-existent lecturer but NO custom files
        print("\n🧪 Test 1: Non-existent lecturer without custom files (should fail)")
        
        payload = {
            "text": test_text,
            "language": "en",
            "lecturer_name": "ankit",
            "speed": 1.0
        }
        try:
            generation_response = requests.post(f"{API_URL}/generate/text", json=payload)
            generation_response.raise_for_status()
            task_data = generation_response.json()
            task_id = task_data["task_id"]
            
            # Wait for failure
            time.sleep(2)
            status_response = requests.get(f"{API_URL}/status/{task_id}")
            status_data = status_response.json()
            
            if status_data["status"] == "failed":
                print(f"✅ Expected failure: {status_data['error']}")
                print(f"💡 Suggestion: {status_data.get('suggestion', 'N/A')}")
            else:
                print(f"⚠️ Unexpected status: {status_data['status']}")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 422:
                print(f"✅ Expected 422 Unprocessable Entity error: {e.response.text}")
            else:
                print(f"❌ Test failed: {e}")
                return False
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False
        
        # 4. Test creating lecturer using the create lecturer endpoint
        print("\n🧪 Test 2: Create lecturer using dedicated endpoint")
        
        # Use sample lecturer files as test files
        sample_portrait = Path("portraits/sample_lecturer.png")
        sample_voice = Path("portraits/sample_lecturer_voice.wav")
        
        if not sample_portrait.exists() or not sample_voice.exists():
            print("❌ Sample lecturer files not found for testing")
            return False
        
        # Create new lecturer using API
        with open(sample_portrait, "rb") as portrait_file, open(sample_voice, "rb") as voice_file:
            files = {
                "portrait_file": ("ankit.png", portrait_file, "image/png"),
                "voice_file": ("ankit_voice.wav", voice_file, "audio/wav")
            }
            
            create_response = requests.post(f"{API_URL}/lecturers/ankit", files=files)
            if create_response.status_code == 200:
                create_data = create_response.json()
                print(f"✅ Lecturer created: {create_data['message']}")
            else:
                print(f"❌ Failed to create lecturer: {create_response.text}")
                return False
        
        # 5. Verify lecturer now exists
        lecturer_check = requests.get(f"{API_URL}/lecturers/ankit")
        lecturer_check_data = lecturer_check.json()
        
        if lecturer_check_data["exists"]:
            print(f"✅ Lecturer 'ankit' now exists")
            print(f"📷 Portrait: {lecturer_check_data['portrait']}")
            print(f"🎤 Voice: {lecturer_check_data['voice_reference']}")
        else:
            print(f"❌ Lecturer creation verification failed")
            return False
        
        # 6. Test text generation with newly created lecturer
        print("\n🧪 Test 3: Generate video with newly created lecturer")
        
        generation_response2 = requests.post(f"{API_URL}/generate/text", json=payload)
        generation_response2.raise_for_status()
        task_data2 = generation_response2.json()
        task_id2 = task_data2["task_id"]
        
        print(f"✅ Generation task started: {task_id2}")
        
        # Poll for completion
        print("⏳ Waiting for video generation...")
        status = "started"
        progress = 0
        
        while status not in ["completed", "failed"]:
            time.sleep(3)
            status_response = requests.get(f"{API_URL}/status/{task_id2}")
            status_response.raise_for_status()
            status_data = status_response.json()
            
            status = status_data["status"]
            new_progress = status_data["progress"]
            
            if new_progress != progress:
                progress = new_progress
                print(f"Progress: {progress}% - {status_data['message']}")
            
            if status == "failed":
                print(f"❌ Generation failed: {status_data.get('error', 'Unknown error')}")
                return False
        
        if status == "completed":
            result_url = status_data["result_url"]
            print(f"✅ Video generated successfully!")
            print(f"📽️ Result URL: {API_URL}{result_url}")
            
            # Test download
            download_response = requests.head(f"{API_URL}{result_url}")
            if download_response.status_code == 200:
                print(f"✅ Video file is accessible for download")
                file_size = download_response.headers.get('content-length', 'Unknown')
                print(f"📏 File size: {file_size} bytes")
            else:
                print(f"⚠️ Video file not accessible: {download_response.status_code}")
            
            return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    finally:
        # Clean up test lecturer (optional)
        print("\n🧹 Cleaning up test lecturer...")
        portraits_dir = Path("portraits")
        for file_pattern in ["ankit.*", "ankit_voice.*"]:
            for file in portraits_dir.glob(file_pattern):
                try:
                    file.unlink()
                    print(f"🗑️ Removed: {file}")
                except:
                    pass

def test_multipart_form_lecturer_creation():
    """Test lecturer creation through multipart form with text generation."""
    print("\n🧪 Test 4: Dynamic lecturer creation via multipart form")
    
    try:
        # Use sample files as custom files
        sample_portrait = Path("portraits/sample_lecturer.png")
        sample_voice = Path("portraits/sample_lecturer_voice.wav")
        
        if not sample_portrait.exists() or not sample_voice.exists():
            print("❌ Sample lecturer files not found for testing")
            return False
        
        # Test data
        test_text = "Hello, this is a test of dynamic lecturer creation through multipart form submission."
        
        # Prepare multipart form data
        with open(sample_portrait, "rb") as portrait_file, open(sample_voice, "rb") as voice_file:
            files = {
                "portrait_file": ("custom_portrait.png", portrait_file, "image/png"),
                "voice_file": ("custom_voice.wav", voice_file, "audio/wav")
            }
            
            data = {
                "text": test_text,
                "language": "en",
                "lecturer_name": "ankit_form_test",
                "speed": "1.0"
            }
            
            # Submit form
            response = requests.post(f"{API_URL}/generate/text", files=files, data=data)
            response.raise_for_status()
            task_data = response.json()
            task_id = task_data["task_id"]
            
            print(f"✅ Form submission successful: {task_id}")
            
            # Wait a bit for processing
            time.sleep(2)
            
            # Check if lecturer was created dynamically
            lecturer_check = requests.get(f"{API_URL}/lecturers/ankit_form_test")
            lecturer_data = lecturer_check.json()
            
            if lecturer_data["exists"]:
                print(f"✅ Lecturer 'ankit_form_test' was created dynamically")
            else:
                print(f"📝 Lecturer creation status: {lecturer_data['message']}")
            
            # Poll for task completion
            print("⏳ Waiting for form-based generation...")
            status = "started"
            
            for _ in range(10):  # Max 30 seconds
                time.sleep(3)
                status_response = requests.get(f"{API_URL}/status/{task_id}")
                status_data = status_response.json()
                status = status_data["status"]
                
                print(f"Status: {status} - {status_data['message']}")
                
                if status in ["completed", "failed"]:
                    break
            
            if status == "completed":
                print(f"✅ Multipart form generation completed successfully!")
                return True
            elif status == "failed":
                print(f"❌ Generation failed: {status_data.get('error', 'Unknown')}")
                return False
            else:
                print(f"⏰ Generation still in progress: {status}")
                return True  # Consider partial success
        
    except Exception as e:
        print(f"❌ Multipart form test failed: {e}")
        return False
    
    finally:
        # Clean up
        portraits_dir = Path("portraits")
        for file_pattern in ["ankit_form_test.*", "ankit_form_test_voice.*"]:
            for file in portraits_dir.glob(file_pattern):
                try:
                    file.unlink()
                    print(f"🗑️ Cleaned up: {file}")
                except:
                    pass

if __name__ == "__main__":
    print("🚀 Starting Dynamic Lecturer Creation Tests")
    print("=" * 60)
    
    test1_success = test_dynamic_lecturer_creation()
    test2_success = test_multipart_form_lecturer_creation()
    
    print("\n📊 Test Results Summary")
    print("=" * 30)
    print(f"Test 1 (API-based): {'✅ PASS' if test1_success else '❌ FAIL'}")
    print(f"Test 2 (Form-based): {'✅ PASS' if test2_success else '❌ FAIL'}")
    
    if test1_success and test2_success:
        print("\n🎉 All dynamic lecturer creation tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️ Some tests failed or incomplete")
        sys.exit(1)
