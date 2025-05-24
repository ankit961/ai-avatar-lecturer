#!/usr/bin/env python3
"""
Test script for generating a Gujarati lecture using the AI Avatar Lecture system.
Demonstrates complete end-to-end functionality with Gujarati content.
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
API_URL = "http://localhost:8000"

def test_gujarati_lecture_generation():
    """Generate a complete lecture in Gujarati and test the end-to-end flow."""
    print("🎓 Creating Gujarati Educational Lecture")
    print("=" * 50)
    
    # Gujarati educational content - a short lecture on programming
    gujarati_lecture = """
    સોફ્ટવેર પ્રોગ્રામિંગ શીખવાની શરૂઆત
    
    આજે આપણે કમ્પ્યૂટર પ્રોગ્રામિંગના મૂળભૂત સિદ્ધાંતો વિશે શીખીશું. પ્રોગ્રામિંગ એ કમ્પ્યુટરને સૂચનાઓ આપવાની કળા છે.
    
    પ્રોગ્રામિંગ ભાષાઓ ત્રણ મુખ્ય પ્રકારમાં વર્ગીકૃત છે:
    ૧) પ્રક્રિયાગત પ્રોગ્રામિંગ
    ૨) ઑબ્જેક્ટ ઓરિએન્ટેડ પ્રોગ્રામિંગ
    ૩) ફંકશનલ પ્રોગ્રામિંગ
    
    દરેક પ્રોગ્રામમાં ડેટા સ્ટ્રકચર્સ અને એલ્ગોરિધમ્સનો ઉપયોગ થાય છે. આ એક અગત્યનો પાયો છે જે દરેક વિદ્યાર્થીએ શીખવો જરૂરી છે.
    """
    
    print("\n📝 Gujarati lecture content:")
    print("-" * 40)
    print(gujarati_lecture)
    
    # 1. Check if backend is responding
    try:
        health_response = requests.get(f"{API_URL}/health")
        health_response.raise_for_status()
        health_data = health_response.json()
        print(f"\n✅ API health check: {health_data['status']}")
    except Exception as e:
        print(f"❌ API health check failed: {e}")
        return False
    
    # 2. Get supported languages
    try:
        languages_response = requests.get(f"{API_URL}/languages")
        languages_response.raise_for_status()
        languages_data = languages_response.json()
        
        if "gu" in languages_data["supported_languages"]:
            print(f"✅ Gujarati language supported: {languages_data['supported_languages']['gu']}")
        else:
            print("⚠️ Gujarati language not explicitly listed in supported languages")
    except Exception as e:
        print(f"❌ Failed to get supported languages: {e}")
    
    # 3. Check available lecturers
    try:
        lecturers_response = requests.get(f"{API_URL}/lecturers")
        lecturers_response.raise_for_status()
        lecturers_data = lecturers_response.json()
        
        if not lecturers_data["lecturers"]:
            print("⚠️ No lecturers found, will use sample_lecturer")
            lecturer_name = "sample_lecturer"
        else:
            lecturer_name = lecturers_data["lecturers"][0]["name"]
            print(f"✅ Found lecturer: {lecturer_name}")
    except Exception as e:
        print(f"❌ Failed to get lecturers: {e}")
        lecturer_name = "sample_lecturer"
    
    # 4. Generate lecture from text
    try:
        print("\n🔊 Generating Gujarati lecture video...")
        
        payload = {
            "text": gujarati_lecture,
            "language": "gu",  # Gujarati 
            "lecturer_name": lecturer_name,
            "speed": 1.0
        }
        
        generation_response = requests.post(
            f"{API_URL}/generate/text",
            json=payload
        )
        generation_response.raise_for_status()
        task_data = generation_response.json()
        
        task_id = task_data["task_id"]
        print(f"✅ Generation task started with ID: {task_id}")
        
        # 5. Poll for task completion
        print("\n⏳ Waiting for generation to complete...")
        status = "started"
        progress = 0
        
        while status not in ["completed", "failed"]:
            status_response = requests.get(f"{API_URL}/status/{task_id}")
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
            
            time.sleep(3)
        
        if status == "completed":
            result_url = status_data["result_url"]
            print(f"✅ Gujarati lecture video generated successfully!")
            print(f"📽️ Result available at: {API_URL}{result_url}")
            
            # Download the video
            output_path = Path("outputs/gujarati_lecture_test.mp4")
            with requests.get(f"{API_URL}{result_url}", stream=True) as r:
                r.raise_for_status()
                with open(output_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            
            print(f"💾 Video downloaded to: {output_path}")
            
            return True
        
    except Exception as e:
        print(f"❌ Gujarati lecture generation failed: {e}")
        return False

if __name__ == "__main__":
    if test_gujarati_lecture_generation():
        print("\n🎉 Gujarati lecture test completed successfully!")
        sys.exit(0)
    else:
        print("\n⚠️ Gujarati lecture test failed")
        sys.exit(1)
