#!/usr/bin/env python3
"""
Test script to generate a video using Ankit's specific portrait and audio files.
This will test the complete workflow with user's custom files.
"""

import asyncio
import json
import logging
import os
import shutil
import sys
import tempfile
from pathlib import Path

# Add the backend directory to sys.path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from app import DoctorAvatarService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_ankit_video_generation():
    """Test video generation using Ankit's portrait and audio files."""
    
    # Initialize the service
    logger.info("Initializing DoctorAvatarService...")
    service = DoctorAvatarService()
    await service.initialize()
    logger.info("Service initialized successfully!")
    
    # Define file paths
    portrait_path = "/Users/ankit_chauhan/Desktop/doctor-avatar/portraits/Ankit Chauhan.png"
    audio_path = "/Users/ankit_chauhan/Desktop/doctor-avatar/portraits/Ankit Chauhan_voice.mp3"
    
    # Check if files exist
    if not os.path.exists(portrait_path):
        logger.error(f"Portrait file not found: {portrait_path}")
        return False
        
    if not os.path.exists(audio_path):
        logger.error(f"Audio file not found: {audio_path}")
        return False
    
    logger.info(f"Using portrait: {portrait_path}")
    logger.info(f"Using audio: {audio_path}")
    
    # Copy files to the backend portraits directory
    backend_portraits = backend_dir / "portraits"
    backend_portraits.mkdir(exist_ok=True)
    
    backend_portrait = backend_portraits / "Ankit Chauhan.png"
    backend_audio = backend_portraits / "Ankit Chauhan_voice.mp3"
    
    shutil.copy2(portrait_path, backend_portrait)
    shutil.copy2(audio_path, backend_audio)
    
    logger.info(f"Files copied to backend directory")
    
    # Test 1: Audio-based video generation (using your voice)
    logger.info("\n" + "="*50)
    logger.info("TEST 1: Audio-based video generation with Ankit's voice")
    logger.info("="*50)
    
    try:
        # Use a sample text that will be converted to your voice
        sample_text = "Hello, my name is Ankit Chauhan. I am testing the doctor avatar system. This technology can help create educational content with personalized avatars and voices."
        
        # Generate video using audio workflow (text -> TTS with your voice -> video)
        with tempfile.TemporaryDirectory() as temp_dir:
            logger.info(f"Processing text: {sample_text[:50]}...")
            
            result = await service.generate_video(
                lecturer_name="Ankit Chauhan",
                text=sample_text,
                target_language="en",  # English
                temp_dir=temp_dir
            )
            
            if result["success"]:
                output_path = result["video_path"]
                file_size = os.path.getsize(output_path) / 1024  # KB
                logger.info(f"✅ Video generated successfully!")
                logger.info(f"📁 Video path: {output_path}")
                logger.info(f"📊 File size: {file_size:.2f} KB")
                
                # Copy to a permanent location
                permanent_path = f"/Users/ankit_chauhan/Desktop/doctor-avatar/ankit_test_video.mp4"
                shutil.copy2(output_path, permanent_path)
                logger.info(f"📋 Video copied to: {permanent_path}")
                
            else:
                logger.error(f"❌ Video generation failed: {result.get('error', 'Unknown error')}")
                return False
                
    except Exception as e:
        logger.error(f"❌ Error in audio-based test: {str(e)}")
        return False
    
    # Test 2: Direct audio file processing
    logger.info("\n" + "="*50)
    logger.info("TEST 2: Direct audio file processing with Ankit's voice")
    logger.info("="*50)
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy the audio file to temp directory
            temp_audio = os.path.join(temp_dir, "input_audio.mp3")
            shutil.copy2(str(backend_audio), temp_audio)
            
            logger.info(f"Processing audio file: {backend_audio}")
            
            result = await service.process_audio_file(
                lecturer_name="Ankit Chauhan",
                audio_file_path=temp_audio,
                target_language="en",
                temp_dir=temp_dir
            )
            
            if result["success"]:
                output_path = result["video_path"]
                file_size = os.path.getsize(output_path) / 1024  # KB
                logger.info(f"✅ Audio processing completed successfully!")
                logger.info(f"📁 Video path: {output_path}")
                logger.info(f"📊 File size: {file_size:.2f} KB")
                
                # Copy to a permanent location
                permanent_path = f"/Users/ankit_chauhan/Desktop/doctor-avatar/ankit_audio_test_video.mp4"
                shutil.copy2(output_path, permanent_path)
                logger.info(f"📋 Video copied to: {permanent_path}")
                
            else:
                logger.error(f"❌ Audio processing failed: {result.get('error', 'Unknown error')}")
                return False
                
    except Exception as e:
        logger.error(f"❌ Error in direct audio test: {str(e)}")
        return False
    
    logger.info("\n" + "="*50)
    logger.info("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
    logger.info("="*50)
    logger.info("✅ Ankit's portrait and voice files are working perfectly")
    logger.info("✅ Both text-to-speech and audio processing workflows are functional")
    logger.info("✅ Video generation with custom lecturer is operational")
    
    return True

async def main():
    """Main function to run the test."""
    logger.info("Starting Ankit's video generation test...")
    
    try:
        success = await test_ankit_video_generation()
        if success:
            logger.info("🎊 Test completed successfully!")
            return 0
        else:
            logger.error("❌ Test failed!")
            return 1
    except Exception as e:
        logger.error(f"💥 Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
