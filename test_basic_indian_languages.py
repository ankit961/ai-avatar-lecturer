#!/usr/bin/env python3
"""
Simple test for basic operations in all supported Indian languages.
Tests text translation, basic TTS, and greeting message creation.
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple, Any

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Import necessary modules
from translate.translate import Translator
from tts.tts import TTSGenerator

# Set up output directory
OUTPUT_DIR = Path("outputs/language_samples")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Simple medical greetings in English to translate to all languages
GREETINGS = {
    "g1": "Hello, I am Dr. Patel. Welcome to today's medical lecture.",
    "g2": "Today we will discuss diabetes and its management.",
    "g3": "Please ask questions if you need any clarification."
}

# Indian languages to test
INDIAN_LANGUAGES = {
    "hi": "Hindi",
    "gu": "Gujarati", 
    "ta": "Tamil",
    "te": "Telugu",
    "mr": "Marathi",
    "bn": "Bengali",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "ur": "Urdu"
}

# TTS supported languages and fallbacks
TTS_FALLBACKS = {
    "hi": "hi",  # Hindi → Hindi (direct)
    "gu": "hi",  # Gujarati → Hindi
    "mr": "hi",  # Marathi → Hindi
    "pa": "hi",  # Punjabi → Hindi
    "bn": "hi",  # Bengali → Hindi
    "te": "hi",  # Telugu → Hindi
    "kn": "hi",  # Kannada → Hindi
    "ml": "hi",  # Malayalam → Hindi
    "ta": "hi",  # Tamil → Hindi
    "ur": "hi"   # Urdu → Hindi
}

def test_basic_translation(translator: Translator):
    """Test translation to all supported languages."""
    print("\n🔠 TESTING BASIC TRANSLATION TO ALL LANGUAGES")
    print("-" * 60)
    
    results = {}
    combined_text = f"{GREETINGS['g1']} {GREETINGS['g2']} {GREETINGS['g3']}"
    
    for lang_code, lang_name in INDIAN_LANGUAGES.items():
        print(f"\n▶️ Testing {lang_name} ({lang_code})...")
        
        try:
            # Translate
            result = translator.translate_text(combined_text, source_lang="en", target_lang=lang_code)
            translated_text = result["translated_text"]
            print(f"  ✅ Translation successful: {translated_text[:50]}...")
            
            # Save translation
            filepath = OUTPUT_DIR / f"{lang_code}_greeting.txt"
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"ENGLISH:\n{combined_text}\n\n{lang_name.upper()}:\n{translated_text}")
            
            print(f"  📝 Saved to: {filepath}")
            
            # Save to results
            results[lang_code] = {
                "name": lang_name,
                "success": True,
                "text": translated_text,
                "file": str(filepath)
            }
            
        except Exception as e:
            print(f"  ❌ Translation failed: {e}")
            results[lang_code] = {
                "name": lang_name,
                "success": False,
                "error": str(e)
            }
    
    return results

def test_basic_tts(tts: TTSGenerator, translations: Dict):
    """Test TTS generation for all languages."""
    print("\n🔊 TESTING BASIC TTS FOR ALL LANGUAGES")
    print("-" * 60)
    
    results = {}
    supported_langs = tts.get_supported_languages()
    print(f"Directly supported TTS languages: {supported_langs}")
    
    for lang_code, translation_info in translations.items():
        lang_name = INDIAN_LANGUAGES[lang_code]
        print(f"\n▶️ Testing {lang_name} ({lang_code})...")
        
        if not translation_info["success"]:
            print(f"  ⏩ Skipping TTS (translation failed)")
            results[lang_code] = {"success": False, "reason": "translation_failed"}
            continue
            
        try:
            # Determine effective language (direct or fallback)
            effective_lang = lang_code
            using_fallback = False
            
            if lang_code not in supported_langs and lang_code in TTS_FALLBACKS:
                effective_lang = TTS_FALLBACKS[lang_code]
                using_fallback = True
                print(f"  ⚠️ Using {INDIAN_LANGUAGES[effective_lang]} as fallback for {lang_name}")
            
            # Generate speech
            output_path = OUTPUT_DIR / f"{lang_code}_greeting.wav"
            
            tts.synthesize_speech(
                text=translation_info["text"],
                output_path=str(output_path),
                language=effective_lang,
                speaker_wav="portraits/sample_lecturer_voice.wav"
            )
            
            print(f"  ✅ Speech generated: {output_path}")
            
            # Save to results
            results[lang_code] = {
                "success": True,
                "using_fallback": using_fallback,
                "fallback_lang": effective_lang if using_fallback else None,
                "file": str(output_path)
            }
            
        except Exception as e:
            print(f"  ❌ TTS generation failed: {e}")
            results[lang_code] = {"success": False, "error": str(e)}
    
    return results

def create_summary(translation_results: Dict, tts_results: Dict):
    """Create a summary of the test results."""
    summary_path = OUTPUT_DIR / "language_support_summary.txt"
    
    translation_success = sum(1 for r in translation_results.values() if r["success"])
    tts_success = sum(1 for r in tts_results.values() if r["success"])
    fallback_count = sum(1 for r in tts_results.values() if r.get("success") and r.get("using_fallback"))
    
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("INDIAN LANGUAGE SUPPORT SUMMARY\n")
        f.write("==============================\n\n")
        f.write(f"Total languages tested: {len(INDIAN_LANGUAGES)}\n")
        f.write(f"Translation success: {translation_success}/{len(INDIAN_LANGUAGES)}\n")
        f.write(f"TTS success: {tts_success}/{len(INDIAN_LANGUAGES)}\n")
        f.write(f"TTS using fallback: {fallback_count}/{tts_success}\n\n")
        f.write("LANGUAGE DETAILS:\n\n")
        
        for lang_code, lang_name in INDIAN_LANGUAGES.items():
            tr_result = translation_results.get(lang_code, {})
            tts_result = tts_results.get(lang_code, {})
            
            f.write(f"{lang_name} ({lang_code}):\n")
            f.write(f"  Translation: {'✅ Success' if tr_result.get('success') else '❌ Failed'}\n")
            
            if tr_result.get('success'):
                if tts_result.get('success'):
                    if tts_result.get('using_fallback'):
                        fallback = INDIAN_LANGUAGES.get(tts_result.get('fallback_lang', ''), 'Unknown')
                        f.write(f"  TTS: ⚠️ Success (with {fallback} fallback)\n")
                    else:
                        f.write(f"  TTS: ✅ Success (native support)\n")
                else:
                    f.write(f"  TTS: ❌ Failed\n")
            
            f.write("\n")
    
    print(f"\n📊 Summary saved to: {summary_path}")
    return summary_path

def main():
    """Run the basic language tests."""
    print("🌏 INDIAN LANGUAGES BASIC TEST")
    print("=============================")
    
    # Initialize components
    print("⏳ Initializing translator...")
    translator = Translator()
    
    print("⏳ Initializing TTS generator...")
    tts_generator = TTSGenerator()
    
    # Test translation
    translation_results = test_basic_translation(translator)
    
    # Test TTS
    tts_results = test_basic_tts(tts_generator, translation_results)
    
    # Create summary
    summary_path = create_summary(translation_results, tts_results)
    
    print("\n✅ All tests completed!")
    print(f"Results saved to: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
