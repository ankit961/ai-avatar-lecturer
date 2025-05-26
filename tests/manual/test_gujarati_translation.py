#!/usr/bin/env python3
"""
Focused test for Gujarati translation capabilities in the AI Avatar Lecture system.
"""

import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from translate.translate import Translator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_gujarati_translation_models():
    """Test English to Gujarati and Gujarati to English translation models."""
    print("🔄 Testing Gujarati Translation Models...")
    
    try:
        translator = Translator()
        
        # Test model loading manually to debug any issues
        print("\nChecking model availability:")
        
        # Check English to Gujarati
        print("\n1. Testing English to Gujarati model:")
        model_name = "Helsinki-NLP/opus-mt-en-gu"
        try:
            print(f"Loading model: {model_name}")
            model_key = "en_to_gu"
            translator._load_model(model_key)
            print(f"✅ Successfully loaded model: {model_name}")
        except Exception as e:
            print(f"❌ Failed to load model {model_name}: {e}")
            # Try alternative model
            print("\nTrying alternative model: Helsinki-NLP/opus-mt-en-inc")
            try:
                translator._load_model("en_to_indic")
                print("✅ Successfully loaded alternative model for English to Gujarati")
            except Exception as e2:
                print(f"❌ Failed to load alternative model: {e2}")
        
        # Check Gujarati to English
        print("\n2. Testing Gujarati to English model:")
        model_name = "Helsinki-NLP/opus-mt-gu-en"
        try:
            print(f"Loading model: {model_name}")
            model_key = "gu_to_en"
            translator._load_model(model_key)
            print(f"✅ Successfully loaded model: {model_name}")
        except Exception as e:
            print(f"❌ Failed to load model {model_name}: {e}")
            # Try alternative model
            print("\nTrying alternative model: Helsinki-NLP/opus-mt-inc-en")
            try:
                translator._load_model("indic_to_en")
                print("✅ Successfully loaded alternative model for Gujarati to English")
            except Exception as e2:
                print(f"❌ Failed to load alternative model: {e2}")
        
        # Test actual translations
        try:
            print("\n3. Testing English to Gujarati translation:")
            english_text = "Welcome to our lecture on artificial intelligence."
            print(f"📝 Original (English): {english_text}")
            
            result = translator.translate_text(english_text, source_lang="en", target_lang="gu")
            gujarati_text = result["translated_text"]
            print(f"📝 Translated (Gujarati): {gujarati_text}")
            print(f"📝 Translation method: {result.get('translation_method', 'standard')}")
        except Exception as e:
            print(f"❌ English to Gujarati translation failed: {e}")
        
        try:
            print("\n4. Testing Gujarati to English translation:")
            gujarati_input = "આજે આપણે કૃત્રિમ બુદ્ધિ વિશે શીખીશું"
            print(f"📝 Original (Gujarati): {gujarati_input}")
            
            result = translator.translate_text(gujarati_input, source_lang="gu", target_lang="en")
            english_back = result["translated_text"]
            print(f"📝 Translated (English): {english_back}")
            print(f"📝 Translation method: {result.get('translation_method', 'standard')}")
        except Exception as e:
            print(f"❌ Gujarati to English translation failed: {e}")
            
        print("\n✅ Gujarati translation model test completed")
        return True
        
    except Exception as e:
        print(f"❌ Gujarati translation model test failed: {e}")
        return False

if __name__ == "__main__":
    test_gujarati_translation_models()
