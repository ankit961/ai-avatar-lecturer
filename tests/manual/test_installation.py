"""
Test script to verify AI Avatar Lecture installation and components.
"""

import sys
import os
from pathlib import Path
import logging

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test if all required modules can be imported."""
    print("🔍 Testing module imports...")
    
    try:
        from asr.asr import ASRProcessor
        print("✅ ASR module imported successfully")
    except Exception as e:
        print(f"❌ ASR module import failed: {e}")
        return False
    
    try:
        from translate.translate import Translator
        print("✅ Translation module imported successfully")
    except Exception as e:
        print(f"❌ Translation module import failed: {e}")
        return False
    
    try:
        from clone.clone import VoiceCloner
        print("✅ Voice cloning module imported successfully")
    except Exception as e:
        print(f"❌ Voice cloning module import failed: {e}")
        return False
    
    try:
        from tts.tts import TTSGenerator
        print("✅ TTS module imported successfully")
    except Exception as e:
        print(f"❌ TTS module import failed: {e}")
        return False
    
    try:
        from video.synthesize_video import SadTalkerWrapper
        print("✅ Video synthesis module imported successfully")
    except Exception as e:
        print(f"❌ Video synthesis module import failed: {e}")
        return False
    
    return True

def test_dependencies():
    """Test if key dependencies are available."""
    print("\n🔍 Testing key dependencies...")
    
    # Test PyTorch
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__} available")
        if torch.cuda.is_available():
            print(f"✅ CUDA available: {torch.cuda.get_device_name()}")
        else:
            print("⚠️  CUDA not available, will use CPU")
    except ImportError:
        print("❌ PyTorch not installed")
        return False
    
    # Test Whisper
    try:
        import whisper
        print("✅ OpenAI Whisper available")
    except ImportError:
        print("❌ OpenAI Whisper not installed")
        return False
    
    # Test Transformers
    try:
        import transformers
        print(f"✅ Transformers {transformers.__version__} available")
    except ImportError:
        print("❌ Transformers not installed")
        return False
    
    # Test TTS
    try:
        from TTS.api import TTS
        print("✅ Coqui TTS available")
    except ImportError:
        print("❌ Coqui TTS not installed")
        return False
    
    # Test FastAPI
    try:
        import fastapi
        print(f"✅ FastAPI {fastapi.__version__} available")
    except ImportError:
        print("❌ FastAPI not installed")
        return False
    
    return True

def test_directories():
    """Test if required directories exist."""
    print("\n🔍 Testing directory structure...")
    
    required_dirs = [
        "asr", "translate", "clone", "tts", "video", "backend",
        "portraits", "uploads", "outputs", "logs"
    ]
    
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if dir_path.exists():
            print(f"✅ {dir_name}/ directory exists")
        else:
            print(f"❌ {dir_name}/ directory missing")
            return False
    
    return True

def test_simple_functionality():
    """Test basic functionality of each module."""
    print("\n🔍 Testing basic functionality...")
    
    try:
        # Test ASR initialization
        from asr.asr import ASRProcessor
        asr = ASRProcessor(model_size="tiny")  # Use tiny model for quick test
        print("✅ ASR processor initialized")
        
        # Test Translator initialization
        from translate.translate import Translator
        translator = Translator()
        print("✅ Translator initialized")
        
        # Test simple translation
        result = translator.translate_text("Hello", source_lang="en", target_lang="hi")
        print(f"✅ Translation test: '{result['translated_text']}'")
        
        # Test TTS initialization (this might download models)
        from tts.tts import TTSGenerator
        print("⏳ Initializing TTS (may download models)...")
        tts = TTSGenerator()
        print("✅ TTS generator initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 AI Avatar Lecture - Installation Test")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Dependencies", test_dependencies),
        ("Directory Structure", test_directories),
        ("Basic Functionality", test_simple_functionality)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Your installation is ready.")
        print("\nNext steps:")
        print("1. Add lecturer portraits and voice samples to portraits/")
        print("2. Start the API server: python backend/app.py")
        print("3. Visit http://localhost:8000/docs for API documentation")
    else:
        print("\n⚠️  Some tests failed. Please check the installation.")
        print("💡 Try running: pip install -r requirements.txt")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
