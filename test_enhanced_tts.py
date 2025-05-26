#!/usr/bin/env python3
"""
Comprehensive test script for Enhanced TTS with all Indian languages.
Tests gTTS, Coqui TTS, and pyttsx3 engines for better language coverage.
"""

import sys
import os
import time
import json
from pathlib import Path
from typing import Dict, List, Tuple

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Import modules
from translate.translate import Translator
from tts.enhanced_tts import EnhancedTTSGenerator

# Set up output directory
OUTPUT_DIR = Path("outputs/enhanced_tts_tests")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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

# Sample text for testing
SAMPLE_TEXT = {
    "greeting": "Hello, welcome to today's medical lecture.",
    "intro": "Today we will discuss diabetes and its management.",
    "content": "Regular monitoring and proper medication are essential for managing diabetes effectively."
}

def test_engine_availability():
    """Test which TTS engines are available."""
    print("🔍 TESTING TTS ENGINE AVAILABILITY")
    print("=" * 50)
    
    tts = EnhancedTTSGenerator()
    engine_info = tts.get_engine_info()
    
    for engine_name, info in engine_info.items():
        status = "✅ Available" if info["available"] else "❌ Not Available"
        print(f"{engine_name.upper()}: {status}")
        if info["available"]:
            print(f"  Languages: {len(info['languages'])} supported")
            print(f"  Voice Cloning: {'Yes' if info['supports_voice_cloning'] else 'No'}")
            if len(info['languages']) <= 10:
                print(f"  Supported: {', '.join(info['languages'])}")
    
    print(f"\nTotal supported languages: {len(tts.get_supported_languages())}")
    print(f"Supported: {', '.join(tts.get_supported_languages())}")
    
    return tts, engine_info

def test_translation_and_tts():
    """Test translation and TTS for all Indian languages."""
    print("\n🌐 TESTING TRANSLATION + ENHANCED TTS")
    print("=" * 50)
    
    # Initialize components
    translator = Translator()
    tts = EnhancedTTSGenerator()
    
    # Combine sample text
    english_text = f"{SAMPLE_TEXT['greeting']} {SAMPLE_TEXT['intro']} {SAMPLE_TEXT['content']}"
    print(f"Original English text: {english_text}")
    
    results = {}
    
    for lang_code, lang_name in INDIAN_LANGUAGES.items():
        print(f"\n{'=' * 60}")
        print(f"TESTING {lang_name.upper()} ({lang_code})")
        print(f"{'=' * 60}")
        
        lang_results = {
            "language_code": lang_code,
            "language_name": lang_name,
            "translation_success": False,
            "translation_text": "",
            "tts_results": {},
            "best_engine": None,
            "errors": []
        }
        
        # Create language-specific output directory
        lang_output_dir = OUTPUT_DIR / lang_code
        lang_output_dir.mkdir(exist_ok=True)
        
        try:
            # 1. Translation Test
            print(f"\n1. 🔄 Testing Translation...")
            translation_result = translator.translate_text(
                english_text, 
                source_lang="en", 
                target_lang=lang_code
            )
            translated_text = translation_result["translated_text"]
            
            # Save translation
            translation_file = lang_output_dir / "translation.txt"
            with open(translation_file, "w", encoding="utf-8") as f:
                f.write(f"ENGLISH:\n{english_text}\n\n")
                f.write(f"{lang_name.upper()}:\n{translated_text}")
            
            print(f"✅ Translation successful")
            print(f"📝 Translated: {translated_text[:100]}...")
            
            lang_results["translation_success"] = True
            lang_results["translation_text"] = translated_text
            
            # 2. TTS Tests with different engines
            print(f"\n2. 🔊 Testing TTS Engines...")
            
            engines_to_test = ['gtts', 'coqui', 'pyttsx3']
            
            for engine in engines_to_test:
                print(f"\n   Testing {engine.upper()} engine...")
                
                try:
                    output_file = lang_output_dir / f"{engine}_speech.wav"
                    
                    start_time = time.time()
                    result_path, engine_used = tts.synthesize_speech(
                        text=translated_text,
                        language=lang_code,
                        output_path=str(output_file),
                        prefer_engine=engine
                    )
                    generation_time = time.time() - start_time
                    
                    # Check if file was created and has content
                    if Path(result_path).exists() and Path(result_path).stat().st_size > 0:
                        print(f"   ✅ {engine.upper()} synthesis successful ({generation_time:.2f}s)")
                        print(f"   📁 Saved to: {result_path}")
                        
                        lang_results["tts_results"][engine] = {
                            "success": True,
                            "engine_used": engine_used,
                            "output_path": result_path,
                            "generation_time": generation_time,
                            "file_size": Path(result_path).stat().st_size
                        }
                        
                        # Set best engine (first successful one)
                        if lang_results["best_engine"] is None:
                            lang_results["best_engine"] = engine
                    else:
                        print(f"   ❌ {engine.upper()} failed - no output file created")
                        lang_results["tts_results"][engine] = {
                            "success": False,
                            "error": "No output file created"
                        }
                
                except Exception as e:
                    print(f"   ❌ {engine.upper()} failed: {e}")
                    lang_results["tts_results"][engine] = {
                        "success": False,
                        "error": str(e)
                    }
            
        except Exception as e:
            print(f"❌ Translation failed: {e}")
            lang_results["errors"].append(f"Translation error: {str(e)}")
        
        results[lang_code] = lang_results
    
    return results

def generate_comprehensive_report(results: Dict, engine_info: Dict):
    """Generate a comprehensive test report."""
    print("\n📊 GENERATING COMPREHENSIVE REPORT")
    print("=" * 50)
    
    # Calculate summary statistics
    total_languages = len(results)
    translation_success = sum(1 for r in results.values() if r["translation_success"])
    
    engine_success_counts = {"gtts": 0, "coqui": 0, "pyttsx3": 0}
    for result in results.values():
        for engine, tts_result in result["tts_results"].items():
            if tts_result.get("success", False):
                engine_success_counts[engine] += 1
    
    # Create summary
    summary = {
        "test_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_languages": total_languages,
        "translation_success": translation_success,
        "engine_availability": engine_info,
        "engine_success_counts": engine_success_counts,
        "fully_supported_languages": []
    }
    
    # Identify fully supported languages
    for lang_code, result in results.items():
        if result["translation_success"] and result["best_engine"]:
            summary["fully_supported_languages"].append({
                "code": lang_code,
                "name": result["language_name"],
                "best_engine": result["best_engine"]
            })
    
    # Generate detailed markdown report
    report_content = f"""# Enhanced TTS Testing Report

## Test Summary
- **Date**: {summary['test_timestamp']}
- **Total Languages Tested**: {total_languages}
- **Translation Success Rate**: {translation_success}/{total_languages} ({translation_success/total_languages*100:.1f}%)
- **Fully Supported Languages**: {len(summary['fully_supported_languages'])}/{total_languages}

## TTS Engine Performance

### Engine Availability
"""
    
    for engine_name, info in engine_info.items():
        status = "✅ Available" if info["available"] else "❌ Not Available"
        report_content += f"- **{engine_name.upper()}**: {status}\n"
        if info["available"]:
            report_content += f"  - Languages: {len(info['languages'])}\n"
            report_content += f"  - Voice Cloning: {'Yes' if info['supports_voice_cloning'] else 'No'}\n"
    
    report_content += f"""
### Engine Success Rates
- **gTTS**: {engine_success_counts['gtts']}/{total_languages} languages
- **Coqui TTS**: {engine_success_counts['coqui']}/{total_languages} languages  
- **pyttsx3**: {engine_success_counts['pyttsx3']}/{total_languages} languages

## Language-by-Language Results

| Language | Code | Translation | gTTS | Coqui | pyttsx3 | Best Engine |
|----------|------|-------------|------|-------|---------|-------------|
"""
    
    for lang_code, result in results.items():
        lang_name = result["language_name"]
        translation_status = "✅" if result["translation_success"] else "❌"
        
        gtts_status = "✅" if result["tts_results"].get("gtts", {}).get("success", False) else "❌"
        coqui_status = "✅" if result["tts_results"].get("coqui", {}).get("success", False) else "❌"
        pyttsx3_status = "✅" if result["tts_results"].get("pyttsx3", {}).get("success", False) else "❌"
        
        best_engine = result["best_engine"] or "None"
        
        report_content += f"| {lang_name} | {lang_code} | {translation_status} | {gtts_status} | {coqui_status} | {pyttsx3_status} | {best_engine} |\n"
    
    report_content += f"""
## Recommendations

### Best Engines for Indian Languages
"""
    
    for lang_info in summary["fully_supported_languages"]:
        report_content += f"- **{lang_info['name']}**: Use {lang_info['best_engine'].upper()}\n"
    
    report_content += f"""
### Implementation Strategy
1. **Primary Choice**: Use gTTS for most Indian languages (better pronunciation)
2. **Fallback**: Use Coqui TTS for voice cloning when available
3. **Offline Option**: Use pyttsx3 for offline scenarios

### Next Steps
1. Integrate enhanced TTS into main application
2. Add engine selection UI options
3. Implement automatic fallback logic
4. Add voice quality assessment metrics

## Files Generated
All test outputs are saved in: `{OUTPUT_DIR}/`
- Translation files: `[lang_code]/translation.txt`
- Audio files: `[lang_code]/[engine]_speech.wav`
"""
    
    # Save report
    report_file = OUTPUT_DIR / "enhanced_tts_report.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_content)
    
    # Save JSON data
    json_file = OUTPUT_DIR / "test_results.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump({
            "summary": summary,
            "detailed_results": results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"📄 Report saved: {report_file}")
    print(f"📊 Data saved: {json_file}")
    
    return summary

def main():
    """Run comprehensive enhanced TTS tests."""
    print("🚀 ENHANCED TTS COMPREHENSIVE TESTING")
    print("=" * 60)
    print("Testing gTTS, Coqui TTS, and pyttsx3 for Indian languages")
    print("=" * 60)
    
    try:
        # Test engine availability
        tts, engine_info = test_engine_availability()
        
        # Test translation and TTS
        results = test_translation_and_tts()
        
        # Generate report
        summary = generate_comprehensive_report(results, engine_info)
        
        print("\n🎉 TESTING COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print(f"Results: {len(summary['fully_supported_languages'])}/{summary['total_languages']} languages fully supported")
        print(f"Report: {OUTPUT_DIR}/enhanced_tts_report.md")
        
        # Print quick summary
        print("\n📋 Quick Summary:")
        for lang_info in summary["fully_supported_languages"]:
            print(f"  ✅ {lang_info['name']}: {lang_info['best_engine']}")
        
    except Exception as e:
        print(f"❌ Testing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
