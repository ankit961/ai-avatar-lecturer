#!/usr/bin/env python3
"""
Test script for generating a minimal Gujarati lecture with proper component initialization.
"""
import os
import sys
import tempfile
import logging
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Import components
from asr.asr import ASRProcessor
from translate.translate import Translator
from tts.tts import TTSGenerator
from video.synthesize_video import SadTalkerWrapper

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_component_initialization():
    """Test proper initialization of all components."""
    print("🔧 Testing component initialization...")
    
    components = {}
    
    try:
        # Initialize ASR
        print("\n1️⃣ Initializing ASR processor...")
        components["asr"] = ASRProcessor()
        print("✅ ASR initialized successfully")
    except Exception as e:
        print(f"❌ ASR initialization failed: {e}")
    
    try:
        # Initialize Translator
        print("\n2️⃣ Initializing Translator...")
        components["translator"] = Translator()
        print("✅ Translator initialized successfully")
    except Exception as e:
        print(f"❌ Translator initialization failed: {e}")
    
    try:
        # Initialize TTS Generator
        print("\n3️⃣ Initializing TTS Generator...")
        components["tts"] = TTSGenerator()
        print("✅ TTS Generator initialized successfully")
    except Exception as e:
        print(f"❌ TTS Generator initialization failed: {e}")
        print(f"Error details: {str(e)}")
    
    try:
        # Initialize Video Synthesizer
        print("\n4️⃣ Initializing SadTalker Video Synthesizer...")
        components["video"] = SadTalkerWrapper()
        print("✅ Video Synthesizer initialized successfully")
    except Exception as e:
        print(f"❌ Video Synthesizer initialization failed: {e}")
    
    return components

def test_minimal_gujarati_generation(components):
    """Test generation of a minimal Gujarati video."""
    print("\n🎬 Testing minimal Gujarati video generation...")
    
    # Skip if essential components are missing
    if "tts" not in components or "video" not in components:
        print("❌ Cannot test video generation - missing essential components")
        return False
    
    try:
        # Sample Gujarati text
        gujarati_text = "નમસ્તે, આજે આપણે કૃત્રિમ બુદ્ધિ વિશે શીખીશું."
        print(f"📝 Gujarati text: {gujarati_text}")
        
        # Create temporary directory for outputs
        output_dir = Path("outputs/gujarati_test")
        output_dir.mkdir(exist_ok=True, parents=True)
        
        # Get lecturer files
        portrait_path = Path("portraits/sample_lecturer.png")
        voice_ref_path = Path("portraits/sample_lecturer_voice.wav")
        
        if not portrait_path.exists() or not voice_ref_path.exists():
            print(f"❌ Missing sample lecturer files")
            return False
        
        # Generate speech
        print("🔊 Generating speech using TTS...")
        audio_path = output_dir / "gujarati_speech.wav"
        
        components["tts"].synthesize_with_cloned_voice(
            text=gujarati_text,
            reference_audio=str(voice_ref_path),
            language="gu",
            output_path=str(audio_path),
            speed=1.0
        )
        
        print(f"✅ Speech generated and saved to {audio_path}")
        
        # Generate video
        print("🎥 Generating video...")
        video_path = output_dir / "gujarati_video.mp4"
        
        components["video"].generate_video(
            portrait_path=str(portrait_path),
            audio_path=str(audio_path),
            output_path=str(video_path)
        )
        
        print(f"✅ Video generated and saved to {video_path}")
        return True
        
    except Exception as e:
        print(f"❌ Gujarati video generation failed: {e}")
        return False

if __name__ == "__main__":
    print("🇮🇳 Testing Gujarati Video Generation with Component Initialization")
    print("=" * 70)
    
    # Initialize components
    components = test_component_initialization()
    
    # Count successful initializations
    successful = sum(1 for _ in components.values())
    print(f"\n✅ Successfully initialized {successful}/4 components")
    
    # Test video generation if enough components are available
    if successful >= 2:
        success = test_minimal_gujarati_generation(components)
        if success:
            print("\n🎉 Gujarati video generation test completed successfully!")
        else:
            print("\n⚠️ Gujarati video generation test failed")
    else:
        print("\n⚠️ Not enough components initialized for video testing")
    
    print("\n💡 Check the output directory for generated files")
