#!/usr/bin/env python3
"""
Test script to debug lip-sync video generation issues.
This will test the SadTalker integration directly.
"""

import logging
import sys
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).parent))

from video.synthesize_video import SadTalkerWrapper
import tempfile
import subprocess

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_sadtalker_direct():
    """Test SadTalker directly using the inference script."""
    # Use sample portrait and a simple test audio
    portrait_path = Path("portraits/sample_lecturer.png")
    
    # Create a simple test audio file using TTS
    test_audio = Path("test_audio.wav")
    
    if not test_audio.exists():
        logger.info("Creating test audio file...")
        # Create a simple test audio using system TTS
        if sys.platform == "darwin":  # macOS
            subprocess.run([
                "say", "-o", str(test_audio), 
                "Hello, this is a test of the lip sync functionality. The avatar should move their lips in sync with this speech."
            ], check=True)
        else:
            logger.error("Please create a test audio file manually: test_audio.wav")
            return False
    
    if not portrait_path.exists():
        logger.error(f"Portrait not found: {portrait_path}")
        return False
    
    logger.info("Testing SadTalker direct inference...")
    
    # Test direct SadTalker inference
    sadtalker_path = Path("SadTalker")
    output_dir = Path("test_output")
    output_dir.mkdir(exist_ok=True)
    
    cmd = [
        "python3", str(sadtalker_path / "inference.py"),
        "--driven_audio", str(test_audio),
        "--source_image", str(portrait_path),
        "--result_dir", str(output_dir),
        "--preprocess", "crop",
        "--size", "256",
        "--enhancer", "gfpgan",
        "--still"
    ]
    
    logger.info(f"Running command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=sadtalker_path,
            capture_output=True,
            text=True,
            check=False
        )
        
        logger.info(f"Return code: {result.returncode}")
        logger.info(f"STDOUT: {result.stdout}")
        if result.stderr:
            logger.error(f"STDERR: {result.stderr}")
        
        # Look for generated video
        video_files = list(output_dir.glob("**/*.mp4"))
        if video_files:
            logger.info(f"Generated video found: {video_files[0]}")
            return True
        else:
            logger.error("No video files generated")
            return False
            
    except Exception as e:
        logger.error(f"Error running SadTalker: {e}")
        return False

def test_wrapper():
    """Test our SadTalker wrapper."""
    logger.info("Testing SadTalker wrapper...")
    
    portrait_path = Path("portraits/sample_lecturer.png")
    test_audio = Path("test_audio.wav")
    
    if not portrait_path.exists() or not test_audio.exists():
        logger.error("Required files missing")
        return False
    
    try:
        # Initialize wrapper
        wrapper = SadTalkerWrapper()
        
        # Generate video
        output_path = Path("test_output/wrapper_test.mp4")
        result = wrapper.generate_video(
            portrait_path=portrait_path,
            audio_path=test_audio,
            output_path=output_path,
            preprocess="crop",
            still=True,
            use_enhancer=True,
            size=256
        )
        
        logger.info(f"Wrapper test result: {result}")
        return Path(result).exists()
        
    except Exception as e:
        logger.error(f"Wrapper test failed: {e}")
        return False

def main():
    """Main test function."""
    logger.info("=== Lip-Sync Video Generation Test ===")
    
    # Test 1: Direct SadTalker
    logger.info("\n1. Testing direct SadTalker inference...")
    direct_success = test_sadtalker_direct()
    
    # Test 2: Wrapper
    logger.info("\n2. Testing SadTalker wrapper...")
    wrapper_success = test_wrapper()
    
    # Results
    logger.info("\n=== Test Results ===")
    logger.info(f"Direct SadTalker: {'✓' if direct_success else '✗'}")
    logger.info(f"Wrapper: {'✓' if wrapper_success else '✗'}")
    
    if direct_success and wrapper_success:
        logger.info("✓ All tests passed - lip-sync should be working")
    elif direct_success:
        logger.info("! Direct SadTalker works, but wrapper has issues")
    else:
        logger.info("✗ SadTalker not working properly")
        
        # Check fallback
        logger.info("Testing fallback video generation...")
        from video.simple_video_fallback import create_static_video
        
        try:
            fallback_output = Path("test_output/fallback_test.mp4")
            create_static_video(
                "portraits/sample_lecturer.png",
                "test_audio.wav", 
                str(fallback_output)
            )
            logger.info(f"✓ Fallback working: {fallback_output}")
        except Exception as e:
            logger.error(f"✗ Fallback also failed: {e}")

if __name__ == "__main__":
    main()
