#!/usr/bin/env python3
"""
Simple test for TTS functionality with Gujarati text
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Import TTS
try:
    from tts.tts import TTSGenerator
    print("TTS module imported successfully")
    
    # Try initializing 
    print("Initializing TTSGenerator...")
    tts = TTSGenerator()
    print(f"TTSGenerator initialized: {tts}")
    
    # Check available models
    if hasattr(tts, 'tts'):
        print("TTS engine available")
        if hasattr(tts.tts, 'languages'):
            print(f"Supported languages: {tts.tts.languages}")
    else:
        print("TTS engine not initialized")
    
    # Try generating speech
    output_path = "outputs/gujarati_test_speech.wav"
    text = "નમસ્તે, આજે આપણે કૃત્રિમ બુદ્ધિ વિશે શીખીશું."
    ref_path = "portraits/sample_lecturer_voice.wav"
    
    print(f"Trying to generate speech with text: {text}")
    result = tts.synthesize_with_cloned_voice(
        text=text,
        reference_audio=ref_path,
        language="gu",
        output_path=output_path,
        speed=1.0
    )
    print(f"Speech generation result: {result}")
    print(f"Output saved to: {output_path}")
    
except ImportError as e:
    print(f"Failed to import TTS module: {e}")
except Exception as e:
    print(f"Error during TTS testing: {e}")
    import traceback
    traceback.print_exc()
