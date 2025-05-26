#!/usr/bin/env python3
"""
Test script to verify translation and TTS functionality for all supported Indian languages.
This script tests English to Indian language translation, TTS generation, and video synthesis.
"""

import sys
import os
import logging
from pathlib import Path
import time
import json

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Import necessary modules
from translate.translate import Translator
from tts.tts import TTSGenerator
from video.synthesize_video import SadTalkerWrapper

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Sample text for translation (medical/educational content)
SAMPLE_ENGLISH_TEXT = {
    "greeting": "Hello, welcome to today's medical lecture.",
    "intro": "Today we will discuss common symptoms and treatments for diabetes.",
    "content": "Diabetes is a chronic condition that affects how your body processes blood sugar. Regular monitoring of glucose levels is essential for management.",
    "conclusion": "Remember to consult with your healthcare provider for personalized advice."
}

# Indian languages to test with their codes
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

# TTS fallback mapping - languages that aren't directly supported in TTS can use these instead
TTS_FALLBACKS = {
    "gu": "hi",  # Gujarati → Hindi
    "mr": "hi",  # Marathi → Hindi
    "pa": "hi",  # Punjabi → Hindi
    "bn": "hi",  # Bengali → Hindi
    "te": "hi",  # Telugu → Hindi
    "kn": "hi",  # Kannada → Hindi
    "ml": "hi"   # Malayalam → Hindi
}

def test_language(lang_code, lang_name):
    """Test translation, TTS, and video generation for a specific language."""
    results = {
        "language_code": lang_code,
        "language_name": lang_name,
        "translation_status": "not_started",
        "tts_status": "not_started",
        "video_status": "not_started",
        "translation_text": "",
        "tts_file": "",
        "video_file": "",
        "errors": []
    }
    
    output_dir = Path(f"outputs/language_tests/{lang_code}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Concatenate sample text
    english_text = f"{SAMPLE_ENGLISH_TEXT['greeting']} {SAMPLE_ENGLISH_TEXT['intro']} {SAMPLE_ENGLISH_TEXT['content']} {SAMPLE_ENGLISH_TEXT['conclusion']}"
    
    print(f"\n{'=' * 80}")
    print(f"TESTING {lang_name.upper()} ({lang_code})")
    print(f"{'=' * 80}")
    
    try:
        # 1. Translation Test
        print(f"\n1. 🔄 Testing English to {lang_name} translation...")
        translator = Translator()
        
        # Translate English to target language
        print(f"📝 Original (English): {english_text}")
        result = translator.translate_text(english_text, source_lang="en", target_lang=lang_code)
        translated_text = result["translated_text"]
        print(f"📝 Translated ({lang_name}): {translated_text}")
        
        # Save translation
        translation_file = output_dir / f"{lang_code}_translation.txt"
        with open(translation_file, "w", encoding="utf-8") as f:
            f.write(f"ENGLISH ORIGINAL:\n{english_text}\n\n{lang_name.upper()} TRANSLATION:\n{translated_text}")
        
        print(f"✅ Translation saved to {translation_file}")
        results["translation_status"] = "success"
        results["translation_text"] = translated_text
        
        # 2. TTS Test
        print(f"\n2. 🔊 Testing Text-to-Speech for {lang_name}...")
        tts_generator = TTSGenerator()
        tts_file = output_dir / f"{lang_code}_speech.wav"
        
        # Check if language is directly supported or needs fallback
        effective_lang = lang_code
        using_fallback = False
        
        if lang_code in TTS_FALLBACKS and lang_code not in tts_generator.get_supported_languages():
            effective_lang = TTS_FALLBACKS[lang_code]
            using_fallback = True
            print(f"⚠️ {lang_name} not directly supported for TTS, using {INDIAN_LANGUAGES[effective_lang]} as fallback")
        
        try:
            tts_generator.synthesize_speech(
                text=translated_text,
                output_path=str(tts_file),
                language=effective_lang,
                speaker_wav="portraits/sample_lecturer_voice.wav"
            )
            print(f"✅ Speech generated at {tts_file}")
            results["tts_status"] = "success" if not using_fallback else "success_with_fallback"
            results["tts_file"] = str(tts_file)
            
            # 3. Video Synthesis Test
            print(f"\n3. 🎬 Testing Video Synthesis for {lang_name}...")
            video_synthesizer = SadTalkerWrapper()
            video_file = output_dir / f"{lang_code}_video.mp4"
            
            try:
                video_synthesizer.generate_video(
                    portrait_path="portraits/sample_lecturer.png",
                    audio_path=str(tts_file),
                    output_path=str(video_file)
                )
                print(f"✅ Video generated at {video_file}")
                results["video_status"] = "success"
                results["video_file"] = str(video_file)
            except Exception as e:
                print(f"❌ Video synthesis failed: {e}")
                results["video_status"] = "failed"
                results["errors"].append(f"Video error: {str(e)}")
        except Exception as e:
            print(f"❌ TTS generation failed: {e}")
            results["tts_status"] = "failed"
            results["errors"].append(f"TTS error: {str(e)}")
    
    except Exception as e:
        print(f"❌ Translation failed: {e}")
        results["translation_status"] = "failed"
        results["errors"].append(f"Translation error: {str(e)}")
    
    return results

def main():
    """Run tests for all Indian languages."""
    print("🌏 INDIAN LANGUAGE SUPPORT TEST")
    print("-------------------------------")
    print(f"Testing {len(INDIAN_LANGUAGES)} languages: {', '.join(INDIAN_LANGUAGES.values())}")
    
    all_results = {}
    summary = {
        "total_languages": len(INDIAN_LANGUAGES),
        "translation_success": 0,
        "tts_success": 0,
        "video_success": 0,
        "fully_supported": 0,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    for lang_code, lang_name in INDIAN_LANGUAGES.items():
        results = test_language(lang_code, lang_name)
        all_results[lang_code] = results
        
        # Update summary
        if results["translation_status"] == "success":
            summary["translation_success"] += 1
        if results["tts_status"] in ["success", "success_with_fallback"]:
            summary["tts_success"] += 1
        if results["video_status"] == "success":
            summary["video_success"] += 1
        if (results["translation_status"] == "success" and
            results["tts_status"] in ["success", "success_with_fallback"] and
            results["video_status"] == "success"):
            summary["fully_supported"] += 1
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total languages tested: {summary['total_languages']}")
    print(f"Translation successful: {summary['translation_success']}/{summary['total_languages']}")
    print(f"TTS generation successful: {summary['tts_success']}/{summary['total_languages']}")
    print(f"Video synthesis successful: {summary['video_success']}/{summary['total_languages']}")
    print(f"Fully supported languages: {summary['fully_supported']}/{summary['total_languages']}")
    
    # Save results
    results_dir = Path("outputs/language_tests")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    with open(results_dir / "test_results.json", "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "details": all_results}, f, indent=2, ensure_ascii=False)
    
    # Generate markdown report
    markdown_report = f"""# Indian Language Support Test Report

## Summary
- **Date**: {summary['timestamp']}
- **Total Languages Tested**: {summary['total_languages']}
- **Translation Success**: {summary['translation_success']}/{summary['total_languages']}
- **TTS Generation Success**: {summary['tts_success']}/{summary['total_languages']}
- **Video Synthesis Success**: {summary['video_success']}/{summary['total_languages']}
- **Fully Supported Languages**: {summary['fully_supported']}/{summary['total_languages']}

## Detailed Results

| Language | Code | Translation | TTS | Video | Notes |
|----------|------|-------------|-----|-------|-------|
"""
    
    for lang_code, result in all_results.items():
        lang_name = INDIAN_LANGUAGES[lang_code]
        translation_status = "✅" if result["translation_status"] == "success" else "❌"
        
        if result["tts_status"] == "success":
            tts_status = "✅"
        elif result["tts_status"] == "success_with_fallback":
            tts_status = "⚠️"
        else:
            tts_status = "❌"
            
        video_status = "✅" if result["video_status"] == "success" else "❌"
        
        notes = []
        if result["tts_status"] == "success_with_fallback":
            notes.append(f"Used {INDIAN_LANGUAGES[TTS_FALLBACKS[lang_code]]} for TTS")
        if result["errors"]:
            notes.append(f"Errors: {len(result['errors'])}")
            
        notes_text = ", ".join(notes) if notes else "-"
        
        markdown_report += f"| {lang_name} | {lang_code} | {translation_status} | {tts_status} | {video_status} | {notes_text} |\n"
    
    markdown_report += """
## Next Steps
- Address TTS support for languages currently using fallbacks
- Improve video synthesis for languages with special characters
- Consider adding more regional accents for widely spoken languages

## Legend
- ✅ Success
- ⚠️ Success with fallback/workaround
- ❌ Failed
"""
    
    with open(results_dir / "indian_languages_report.md", "w", encoding="utf-8") as f:
        f.write(markdown_report)
    
    print(f"\nDetailed results saved to {results_dir/'test_results.json'}")
    print(f"Markdown report saved to {results_dir/'indian_languages_report.md'}")

if __name__ == "__main__":
    main()
