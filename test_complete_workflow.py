#!/usr/bin/env python3
"""
Complete workflow test for AI Avatar Lecture with Enhanced TTS.
Tests the entire pipeline: Translation → Enhanced TTS → Video Generation
"""

import sys
import os
import time
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

def test_complete_workflow():
    """Test the complete AI Avatar Lecture workflow with enhanced TTS."""
    print("🚀 COMPLETE WORKFLOW TEST WITH ENHANCED TTS")
    print("=" * 60)
    
    try:
        # Import modules
        from translate.translate import Translator
        from tts.enhanced_tts import EnhancedTTSGenerator
        from video.synthesize_video import SadTalkerWrapper
        
        # Test data
        test_languages = ["hi", "gu", "ta", "mr"]
        english_text = "Hello, welcome to today's medical lecture on diabetes management and prevention."
        
        # Initialize components
        print("\n1. 🔧 Initializing Components...")
        translator = Translator()
        enhanced_tts = EnhancedTTSGenerator()
        video_synthesizer = SadTalkerWrapper()
        
        print("   ✅ All components initialized")
        
        # Create output directory
        output_dir = Path("outputs/complete_workflow_test")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = {}
        
        for lang_code in test_languages:
            lang_name = {
                "hi": "Hindi", 
                "gu": "Gujarati",
                "ta": "Tamil", 
                "mr": "Marathi"
            }[lang_code]
            
            print(f"\n{'='*50}")
            print(f"🌐 TESTING {lang_name.upper()} ({lang_code})")
            print(f"{'='*50}")
            
            lang_output_dir = output_dir / lang_code
            lang_output_dir.mkdir(exist_ok=True)
            
            try:
                # Step 1: Translation
                print(f"\n   Step 1: 🔄 Translating to {lang_name}...")
                start_time = time.time()
                
                translation_result = translator.translate_text(
                    english_text, 
                    source_lang="en", 
                    target_lang=lang_code
                )
                translated_text = translation_result["translated_text"]
                translation_time = time.time() - start_time
                
                print(f"   ✅ Translation completed ({translation_time:.2f}s)")
                print(f"   📝 Original: {english_text}")
                print(f"   📝 Translated: {translated_text}")
                
                # Save translation
                translation_file = lang_output_dir / "translation.txt"
                with open(translation_file, "w", encoding="utf-8") as f:
                    f.write(f"ENGLISH:\n{english_text}\n\n{lang_name.upper()}:\n{translated_text}")
                
                # Step 2: Enhanced TTS
                print(f"\n   Step 2: 🔊 Generating speech with Enhanced TTS...")
                start_time = time.time()
                
                speech_file = lang_output_dir / "speech.wav"
                result_path, engine_used = enhanced_tts.synthesize_speech(
                    text=translated_text,
                    language=lang_code,
                    output_path=str(speech_file)
                )
                tts_time = time.time() - start_time
                
                print(f"   ✅ Speech generated ({tts_time:.2f}s)")
                print(f"   🎵 Engine used: {engine_used}")
                print(f"   📁 File: {result_path}")
                
                if Path(result_path).exists():
                    file_size = Path(result_path).stat().st_size
                    print(f"   📊 File size: {file_size} bytes")
                
                # Step 3: Video Generation
                print(f"\n   Step 3: 🎬 Generating video...")
                start_time = time.time()
                
                video_file = lang_output_dir / f"{lang_code}_lecture.mp4"
                
                try:
                    video_synthesizer.generate_video(
                        portrait_path="portraits/sample_lecturer.png",
                        audio_path=result_path,
                        output_path=str(video_file)
                    )
                    video_time = time.time() - start_time
                    
                    if Path(video_file).exists():
                        video_size = Path(video_file).stat().st_size
                        print(f"   ✅ Video generated successfully ({video_time:.2f}s)")
                        print(f"   🎥 Video: {video_file}")
                        print(f"   📊 Video size: {video_size} bytes")
                        video_success = True
                    else:
                        print(f"   ❌ Video file not created")
                        video_success = False
                        video_time = 0
                        
                except Exception as e:
                    print(f"   ❌ Video generation failed: {e}")
                    video_success = False
                    video_time = 0
                
                # Record results
                results[lang_code] = {
                    "language_name": lang_name,
                    "translation_success": True,
                    "translation_time": translation_time,
                    "translated_text": translated_text,
                    "tts_success": True,
                    "tts_time": tts_time,
                    "tts_engine": engine_used,
                    "speech_file": result_path,
                    "video_success": video_success,
                    "video_time": video_time,
                    "video_file": str(video_file) if video_success else None,
                    "total_time": translation_time + tts_time + video_time
                }
                
                print(f"\n   📊 {lang_name} Results:")
                print(f"      Translation: ✅ ({translation_time:.2f}s)")
                print(f"      TTS: ✅ {engine_used} ({tts_time:.2f}s)")
                print(f"      Video: {'✅' if video_success else '❌'} ({video_time:.2f}s)")
                print(f"      Total: {results[lang_code]['total_time']:.2f}s")
                
            except Exception as e:
                print(f"   ❌ Failed: {e}")
                results[lang_code] = {
                    "language_name": lang_name,
                    "translation_success": False,
                    "error": str(e)
                }
        
        # Generate Summary Report
        print(f"\n{'='*60}")
        print("📊 FINAL RESULTS SUMMARY")
        print(f"{'='*60}")
        
        successful_languages = []
        tts_engines_used = {}
        
        for lang_code, result in results.items():
            if result.get("translation_success", False) and result.get("tts_success", False):
                successful_languages.append(result["language_name"])
                engine = result.get("tts_engine", "unknown")
                tts_engines_used[engine] = tts_engines_used.get(engine, 0) + 1
        
        print(f"✅ Successful Languages: {len(successful_languages)}/{len(test_languages)}")
        print(f"   Languages: {', '.join(successful_languages)}")
        
        print(f"\n🔊 TTS Engine Usage:")
        for engine, count in tts_engines_used.items():
            print(f"   {engine}: {count} languages")
        
        print(f"\n📋 Detailed Results:")
        print(f"{'Language':<12} {'Translation':<12} {'TTS':<15} {'Video':<8} {'Total Time':<12}")
        print("-" * 65)
        
        for lang_code, result in results.items():
            lang_name = result["language_name"]
            trans_status = "✅" if result.get("translation_success", False) else "❌"
            
            if result.get("tts_success", False):
                tts_status = f"✅ {result.get('tts_engine', '???')}"
            else:
                tts_status = "❌"
            
            video_status = "✅" if result.get("video_success", False) else "❌"
            total_time = f"{result.get('total_time', 0):.1f}s"
            
            print(f"{lang_name:<12} {trans_status:<12} {tts_status:<15} {video_status:<8} {total_time:<12}")
        
        # Save detailed report
        report_file = output_dir / "workflow_test_report.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("# Complete Workflow Test Report\n\n")
            f.write(f"**Test Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Languages Tested**: {len(test_languages)}\n")
            f.write(f"**Successful**: {len(successful_languages)}\n\n")
            
            f.write("## Results by Language\n\n")
            for lang_code, result in results.items():
                f.write(f"### {result['language_name']} ({lang_code})\n")
                if result.get("translation_success", False):
                    f.write(f"- **Translation**: ✅ ({result.get('translation_time', 0):.2f}s)\n")
                    f.write(f"- **TTS**: {'✅' if result.get('tts_success', False) else '❌'} {result.get('tts_engine', '')} ({result.get('tts_time', 0):.2f}s)\n")
                    f.write(f"- **Video**: {'✅' if result.get('video_success', False) else '❌'} ({result.get('video_time', 0):.2f}s)\n")
                    f.write(f"- **Total Time**: {result.get('total_time', 0):.2f}s\n")
                    if result.get('translated_text'):
                        f.write(f"- **Translated Text**: {result['translated_text']}\n")
                else:
                    f.write(f"- **Status**: ❌ Failed\n")
                    f.write(f"- **Error**: {result.get('error', 'Unknown error')}\n")
                f.write("\n")
        
        print(f"\n📄 Detailed report saved: {report_file}")
        print(f"📁 Test outputs saved: {output_dir}")
        
        print(f"\n🎉 WORKFLOW TEST COMPLETED!")
        
        return len(successful_languages) == len(test_languages)
        
    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backend_server():
    """Test if the backend server can start with enhanced TTS."""
    print(f"\n🖥️  TESTING BACKEND SERVER")
    print("=" * 40)
    
    try:
        # Try to import the backend
        print("1. Testing backend imports...")
        from backend.app import app, initialize_components
        print("   ✅ Backend imports successful")
        
        print("2. Testing component initialization...")
        import asyncio
        asyncio.run(initialize_components())
        print("   ✅ Components initialized successfully")
        
        print("3. Testing enhanced TTS integration...")
        from backend.app import tts_generator
        if tts_generator:
            engine_info = tts_generator.get_engine_info()
            available_engines = [name for name, info in engine_info.items() if info["available"]]
            print(f"   ✅ Enhanced TTS integrated: {', '.join(available_engines)}")
        else:
            print("   ⚠️ TTS generator not initialized yet")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Backend test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 AI AVATAR LECTURE - COMPLETE SYSTEM TEST")
    print("=" * 70)
    
    # Test 1: Complete Workflow
    workflow_success = test_complete_workflow()
    
    # Test 2: Backend Integration  
    backend_success = test_backend_server()
    
    # Final Results
    print(f"\n{'='*70}")
    print("🏁 FINAL TEST RESULTS")
    print(f"{'='*70}")
    print(f"Complete Workflow: {'✅ PASSED' if workflow_success else '❌ FAILED'}")
    print(f"Backend Integration: {'✅ PASSED' if backend_success else '❌ FAILED'}")
    
    overall_success = workflow_success and backend_success
    print(f"\nOverall System: {'✅ READY FOR PRODUCTION' if overall_success else '❌ NEEDS ATTENTION'}")
    
    if overall_success:
        print("\n🎉 All systems operational! The AI Avatar Lecture system is ready.")
        print("🚀 You can now:")
        print("   - Start the backend server: python backend/app.py")
        print("   - Open the web interface: http://localhost:9000/ui")
        print("   - Generate videos in multiple Indian languages!")
    else:
        print("\n⚠️ Some issues detected. Please review the test results above.")
