#!/usr/bin/env python3
"""
Simple script to generate and save Gujarati translations
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Import translator
from translate.translate import Translator

def main():
    # Sample English lecture content
    english_content = """
    Welcome to our computer science lecture.
    Today we will learn about machine learning algorithms.
    Artificial intelligence is transforming education.
    Let's explore the fundamentals of programming.
    Mathematics is the foundation of computer science.
    """
    
    print("Original English content:")
    print("-" * 40)
    print(english_content)
    
    # Initialize translator
    print("\nInitializing translator...")
    translator = Translator()
    
    # Translate to Gujarati
    print("\nTranslating to Gujarati...")
    result = translator.translate_text(english_content, source_lang="en", target_lang="gu")
    gujarati_text = result["translated_text"]
    
    print("\nGujarati translation:")
    print("-" * 40)
    print(gujarati_text)
    
    # Save translations to file
    output_dir = Path("outputs/translations")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "english_to_gujarati.txt"
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("ENGLISH ORIGINAL:\n")
        f.write(english_content)
        f.write("\n\nGUJARATI TRANSLATION:\n")
        f.write(gujarati_text)
        f.write("\n")
    
    print(f"\nTranslations saved to: {output_file}")
    
    # Also do back translation for verification
    print("\nPerforming back-translation to English...")
    back_result = translator.translate_text(gujarati_text, source_lang="gu", target_lang="en")
    back_english = back_result["translated_text"]
    
    print("\nBack-translated to English:")
    print("-" * 40)
    print(back_english)
    
    with open(output_file, "a", encoding="utf-8") as f:
        f.write("\n\nBACK-TRANSLATION TO ENGLISH:\n")
        f.write(back_english)
        f.write("\n")
    
    print("\nTranslation process completed successfully!")

if __name__ == "__main__":
    main()
