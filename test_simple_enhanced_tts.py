#!/usr/bin/env python3
"""
Simple test for enhanced TTS with Gujarati
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

try:
    from tts.enhanced_tts import EnhancedTTSGenerator
    
    print("🧪 Testing Enhanced TTS with Gujarati")
    print("=" * 40)
    
    # Initialize enhanced TTS
    print("1. Initializing Enhanced TTS...")
    tts = EnhancedTTSGenerator()
    
    # Check engine availability
    print("\n2. Checking available engines...")
    engine_info = tts.get_engine_info()
    for engine, info in engine_info.items():
        status = "✅" if info["available"] else "❌"
        print(f"   {engine}: {status}")
    
    # Test with Gujarati text
    print("\n3. Testing Gujarati speech synthesis...")
    gujarati_text = "નમસ્તે, આજે આપણે કૃત્રિમ બુદ્ધિ વિશે શીખીશું."
    
    # Try different engines
    engines = ["gtts", "coqui", "pyttsx3"]
    
    for engine in engines:
        print(f"\n   Testing {engine.upper()}...")
        try:
            output_path = f"outputs/test_{engine}_gujarati.wav"
            Path("outputs").mkdir(exist_ok=True)
            
            result_path, engine_used = tts.synthesize_speech(
                text=gujarati_text,
                language="gu",
                output_path=output_path,
                prefer_engine=engine
            )
            
            if Path(result_path).exists():
                file_size = Path(result_path).stat().st_size
                print(f"   ✅ Success! File: {result_path} ({file_size} bytes)")
                print(f"   Engine used: {engine_used}")
            else:
                print(f"   ❌ Failed - no output file")
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n✅ Test completed!")
    
except Exception as e:
    print(f"❌ Failed to test enhanced TTS: {e}")
    import traceback
    traceback.print_exc()
