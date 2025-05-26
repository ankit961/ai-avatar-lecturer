#!/usr/bin/env python3
"""
Simple test to generate a video with Ankit's files and monitor progress.
"""

import requests
import time
import os
from pathlib import Path

def test_video_generation():
    """Test video generation with proper monitoring."""
    
    base_url = "http://localhost:9000"
    
    print("🎬 Starting video generation with Ankit Chauhan...")
    print("=" * 60)
    
    # Prepare the form data
    data = {
        "text": "Hello! This is Ankit testing the AI avatar system. This technology can create realistic talking avatars using my portrait and voice.",
        "language": "en", 
        "lecturer_name": "Ankit Chauhan",
        "speed": "1.0"
    }
    
    print(f"📝 Text: {data['text'][:50]}...")
    print(f"👤 Lecturer: {data['lecturer_name']}")
    print(f"🌐 Language: {data['language']}")
    print()
    
    try:
        print("🚀 Sending request to backend...")
        start_time = time.time()
        
        # Send the request with a longer timeout
        response = requests.post(f"{base_url}/generate/text", data=data, timeout=600)  # 10 minutes
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"⏱️  Request completed in {duration:.2f} seconds")
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result.get('success', False)}")
            print(f"📁 Task ID: {result.get('task_id', 'N/A')}")
            
            if 'video_path' in result:
                video_path = result['video_path']
                print(f"🎥 Video path: {video_path}")
                
                # Check if file exists and get size
                if os.path.exists(video_path):
                    file_size = os.path.getsize(video_path) / 1024  # KB
                    print(f"📊 File size: {file_size:.2f} KB")
                    
                    # Copy to desktop for easy access
                    desktop_path = "/Users/ankit_chauhan/Desktop/ankit_avatar_video.mp4"
                    import shutil
                    shutil.copy2(video_path, desktop_path)
                    print(f"📋 Video copied to desktop: {desktop_path}")
                    
                    print("🎉 VIDEO GENERATION SUCCESSFUL!")
                    return True
                else:
                    print(f"❌ Video file not found at: {video_path}")
            
            if 'audio_path' in result:
                print(f"🔊 Audio path: {result['audio_path']}")
                
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out after 10 minutes")
        print("💡 This might be normal for video generation - checking outputs directory...")
        
        # Check if output was created anyway
        outputs_dir = Path("/Users/ankit_chauhan/Desktop/doctor-avatar/backend/outputs")
        latest_dirs = sorted(outputs_dir.glob("text_*"), key=lambda x: x.stat().st_mtime, reverse=True)
        
        if latest_dirs:
            latest_dir = latest_dirs[0]
            print(f"📁 Latest output directory: {latest_dir}")
            
            # Look for video files
            video_files = list(latest_dir.rglob("*.mp4"))
            if video_files:
                for video_file in video_files:
                    file_size = video_file.stat().st_size / 1024
                    print(f"🎥 Found video: {video_file} ({file_size:.2f} KB)")
                    
                    # Copy to desktop
                    desktop_path = f"/Users/ankit_chauhan/Desktop/ankit_avatar_video_{video_file.name}"
                    import shutil
                    shutil.copy2(str(video_file), desktop_path)
                    print(f"📋 Video copied to: {desktop_path}")
                    
                return True
        
        return False
        
    except Exception as e:
        print(f"💥 Error: {str(e)}")
        return False
    
    return False

if __name__ == "__main__":
    print("🚀 Testing Ankit's Avatar Video Generation")
    print("=" * 60)
    
    success = test_video_generation()
    
    if success:
        print("\n🎊 Test completed successfully!")
        print("✅ Your personalized avatar video has been generated!")
    else:
        print("\n❌ Test encountered issues")
        print("💡 Check the backend logs for more details")
