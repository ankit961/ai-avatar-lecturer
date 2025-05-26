#!/usr/bin/env python3
"""
Quick test for key Indian languages with enhanced TTS
"""
import sys
from pathlib import Path
import time

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from translate.translate import Translator
from tts.enhanced_tts import EnhancedTTSGenerator

# Test subset of languages
TEST_LANGUAGES = {
    "hi": "Hindi",
    "gu": "Gujarati", 
    "ta": "Tamil",
    "mr": "Marathi",
    "bn": "Bengali"
}

def test_key_languages():
    """Test key Indian languages with enhanced TTS."""
    print("🚀 TESTING KEY INDIAN LANGUAGES")
    print("=" * 40)
    
    # Initialize components
    translator = Translator()
    tts = EnhancedTTSGenerator()
    
    # Sample text
    english_text = "Hello, welcome to today's medical lecture on diabetes management."
    
    results = {}
    
    for lang_code, lang_name in TEST_LANGUAGES.items():
        print(f"\n🔍 Testing {lang_name} ({lang_code})...")
        
        try:
            # Translation
            print("  1. Translating...")
            result = translator.translate_text(english_text, "en", lang_code)
            translated_text = result["translated_text"]
            print(f"     ✅ Translation: {translated_text[:50]}...")
            
            # TTS with different engines
            print("  2. Testing TTS engines...")
            
            engines = ["gtts", "coqui"]
            tts_results = {}
            
            for engine in engines:
                try:
                    output_file = f"outputs/quick_test_{lang_code}_{engine}.wav"
                    
                    start_time = time.time()
                    result_path, engine_used = tts.synthesize_speech(
                        text=translated_text,
                        language=lang_code,
                        output_path=output_file,
                        prefer_engine=engine
                    )
                    duration = time.time() - start_time
                    
                    if Path(result_path).exists():
                        file_size = Path(result_path).stat().st_size
                        print(f"     ✅ {engine}: Success ({duration:.1f}s, {file_size} bytes, used {engine_used})")
                        tts_results[engine] = True
                    else:
                        print(f"     ❌ {engine}: Failed - no file")
                        tts_results[engine] = False
                
                except Exception as e:
                    print(f"     ❌ {engine}: Error - {e}")
                    tts_results[engine] = False
            
            results[lang_code] = {
                "translation": True,
                "translated_text": translated_text,
                "tts_results": tts_results
            }
            
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            results[lang_code] = {"translation": False, "error": str(e)}
    
    # Summary
    print(f"\n📊 SUMMARY")
    print("=" * 40)
    for lang_code, result in results.items():
        lang_name = TEST_LANGUAGES[lang_code]
        if result.get("translation", False):
            gtts_status = "✅" if result["tts_results"].get("gtts", False) else "❌"
            coqui_status = "✅" if result["tts_results"].get("coqui", False) else "❌"
            print(f"{lang_name:12} | Translation: ✅ | gTTS: {gtts_status} | Coqui: {coqui_status}")
        else:
            print(f"{lang_name:12} | Translation: ❌")
    
    return results

if __name__ == "__main__":
    test_key_languages()
