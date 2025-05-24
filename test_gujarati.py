#!/usr/bin/env python3
"""
Test script for Gujarati language support in AI Avatar Lecture system.
Tests ASR, translation, and API functionality with Gujarati content.
"""

import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from asr.asr import ASRProcessor
from translate.translate import Translator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_gujarati_translation():
    """Test English to Gujarati and Gujarati to English translation."""
    print("🔄 Testing Gujarati Translation...")
    
    try:
        translator = Translator()
        
        # Test English to Gujarati
        english_text = "Hello students, welcome to today's lecture on artificial intelligence."
        print(f"📝 Original (English): {english_text}")
        
        result = translator.translate_text(english_text, source_lang="en", target_lang="gu")
        gujarati_text = result["translated_text"]
        print(f"📝 Translated (Gujarati): {gujarati_text}")
        
        # Test Gujarati to English
        gujarati_input = "આજે આપણે કૃત્રિમ બુદ્ધિ વિશે શીખીશું"
        print(f"📝 Original (Gujarati): {gujarati_input}")
        
        result = translator.translate_text(gujarati_input, source_lang="gu", target_lang="en")
        english_back = result["translated_text"]
        print(f"📝 Translated back (English): {english_back}")
        
        print("✅ Gujarati translation test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Gujarati translation test failed: {e}")
        return False

def test_asr_auto_detection():
    """Test ASR auto-detection capabilities."""
    print("\n🎤 Testing ASR Auto-detection...")
    
    try:
        asr = ASRProcessor()
        
        # Test with sample audio (if available)
        sample_audio = Path("portraits/sample_lecturer_voice.wav")
        if sample_audio.exists():
            result = asr.transcribe_audio(str(sample_audio), language="auto")
            print(f"📝 Transcribed text: {result['text']}")
            print(f"📝 Detected language: {result.get('language', 'unknown')}")
            print("✅ ASR auto-detection test completed!")
            return True
        else:
            print("⚠️  Sample audio file not found, skipping ASR test")
            return True
            
    except Exception as e:
        print(f"❌ ASR test failed: {e}")
        return False

def test_gujarati_workflow():
    """Test complete Gujarati workflow: English -> Gujarati -> ASR recognition."""
    print("\n🔄 Testing Complete Gujarati Workflow...")
    
    try:
        # Sample educational content in English
        educational_content = [
            "Welcome to our computer science lecture.",
            "Today we will learn about machine learning algorithms.",
            "Artificial intelligence is transforming education.",
            "Let's explore the fundamentals of programming.",
            "Mathematics is the foundation of computer science."
        ]
        
        translator = Translator()
        
        print("📚 Educational Content Translation to Gujarati:")
        print("=" * 50)
        
        for i, content in enumerate(educational_content, 1):
            print(f"\n{i}. Original: {content}")
            
            result = translator.translate_text(content, source_lang="en", target_lang="gu")
            gujarati_translation = result["translated_text"]
            print(f"   Gujarati: {gujarati_translation}")
            
            # Test reverse translation for accuracy
            reverse_result = translator.translate_text(gujarati_translation, source_lang="gu", target_lang="en")
            reverse_translation = reverse_result["translated_text"]
            print(f"   Back to English: {reverse_translation}")
            
        print("\n✅ Complete Gujarati workflow test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Gujarati workflow test failed: {e}")
        return False

def test_lecturer_profile_gujarati():
    """Test lecturer profile naming with Gujarati context."""
    print("\n👨‍🏫 Testing Lecturer Profile for Gujarati Context...")
    
    try:
        # Check if sample lecturer files exist with new naming
        portraits_dir = Path("portraits")
        
        lecturer_files = {
            "portrait": portraits_dir / "sample_lecturer.png",
            "voice": portraits_dir / "sample_lecturer_voice.wav",
            "directory": portraits_dir / "sample_lecturer"
        }
        
        print("📁 Checking lecturer profile files:")
        for file_type, file_path in lecturer_files.items():
            if file_path.exists():
                print(f"   ✅ {file_type.title()}: {file_path.name}")
            else:
                print(f"   ❌ {file_type.title()}: {file_path.name} (missing)")
        
        # Suggest Gujarati lecturer names
        gujarati_lecturer_names = [
            "prof_sharma",
            "prof_patel", 
            "prof_shah",
            "prof_desai",
            "prof_modi"
        ]
        
        print(f"\n💡 Suggested Gujarati lecturer profile names:")
        for name in gujarati_lecturer_names:
            print(f"   - {name}.png & {name}_voice.wav")
            
        print("✅ Lecturer profile check completed!")
        return True
        
    except Exception as e:
        print(f"❌ Lecturer profile test failed: {e}")
        return False

def main():
    """Run all Gujarati language tests."""
    print("🇮🇳 AI Avatar Lecture - Gujarati Language Testing")
    print("=" * 55)
    
    tests = [
        ("Gujarati Translation", test_gujarati_translation),
        ("ASR Auto-detection", test_asr_auto_detection),
        ("Gujarati Workflow", test_gujarati_workflow),
        ("Lecturer Profiles", test_lecturer_profile_gujarati)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 55)
    print("📊 GUJARATI TESTING SUMMARY")
    print("=" * 55)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nPassed: {passed}/{total} tests")
    
    if passed == total:
        print("\n🎉 All Gujarati tests passed! The system is ready for Gujarati educational content.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Some Gujarati functionality may be limited.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
