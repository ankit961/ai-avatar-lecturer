#!/usr/bin/env python3
"""
Core functionality test for Gujarati support in AI Avatar Lecture
"""
import sys
from pathlib import Path
import json

# Add project root to path
sys.path.append(str(Path(__file__).parent))

def test_gujarati_core():
    """Test core Gujarati functionality without dependency issues"""
    
    print("🇮🇳 AI Avatar Lecture - Gujarati Core Functionality Test")
    print("=" * 60)
    
    # Load sample Gujarati text
    sample_path = Path("test_data/gujarati_lecture.txt")
    if not sample_path.exists():
        print("❌ Gujarati sample text file not found.")
        return False
    
    with open(sample_path, 'r', encoding='utf-8') as f:
        gujarati_text = f.read().strip()
    
    print("\n📝 Loaded Gujarati sample text:")
    print("-" * 40)
    print(gujarati_text)
    print("-" * 40)
    
    # Test translation module
    print("\n🔄 Testing Gujarati translation...")
    try:
        from translate.translate import Translator
        
        translator = Translator()
        
        # Translate Gujarati to English
        print("\n1. Gujarati → English translation:")
        result = translator.translate_text(gujarati_text, source_lang="gu", target_lang="en")
        english_text = result["translated_text"]
        
        print(f"\nOriginal Gujarati:")
        print(gujarati_text[:100] + "..." if len(gujarati_text) > 100 else gujarati_text)
        
        print(f"\nTranslated to English:")
        print(english_text[:100] + "..." if len(english_text) > 100 else english_text)
        
        # Translate English back to Gujarati
        print("\n2. English → Gujarati translation:")
        result = translator.translate_text(english_text, source_lang="en", target_lang="gu")
        back_to_gujarati = result["translated_text"]
        
        print(f"\nTranslated back to Gujarati:")
        print(back_to_gujarati[:100] + "..." if len(back_to_gujarati) > 100 else back_to_gujarati)
        
        print("\n✅ Translation module works with Gujarati")
        
    except Exception as e:
        print(f"\n❌ Translation test failed: {e}")
    
    # Test output capabilities
    print("\n📂 Saving test results...")
    
    output_dir = Path("outputs/gujarati_test")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Save to file for verification
    result_file = output_dir / "translation_results.json"
    
    try:
        results = {
            "original_gujarati": gujarati_text,
            "translated_english": english_text,
            "back_translated_gujarati": back_to_gujarati
        }
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        print(f"✅ Results saved to {result_file}")
        
    except Exception as e:
        print(f"❌ Failed to save results: {e}")
    
    print("\n🎉 Gujarati core functionality test completed!")
    return True

if __name__ == "__main__":
    test_gujarati_core()
