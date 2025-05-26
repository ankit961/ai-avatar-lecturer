#!/usr/bin/env python3
"""
Script to generate a lecturer video with Gujarati content.
Uses the translation module for English to Gujarati translation,
then generates video using the SadTalker-based video synthesis.
"""

import sys
import os
import logging
import argparse
from pathlib import Path

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

def create_gujarati_lecture_video(
    english_text: str,
    output_dir: str = "outputs/gujarati_demo",
    lecturer_name: str = "sample_lecturer",
    intermediate_files: bool = True
):
    """
    Create a Gujarati lecture video from English text.
    
    Args:
        english_text: English text content for the lecture
        output_dir: Directory to save output files
        lecturer_name: Name of the lecturer profile to use
        intermediate_files: Whether to keep intermediate files
    
    Returns:
        Path to the generated video
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Initialize components
    logger.info("Initializing components...")
    translator = Translator()
    
    # Step 2: Translate English to Gujarati
    logger.info("Translating English to Gujarati...")
    translation_result = translator.translate_text(
        english_text, 
        source_lang="en", 
        target_lang="gu"
    )
    gujarati_text = translation_result["translated_text"]
    
    # Save translated text
    translation_file = output_path / "gujarati_translation.txt"
    with open(translation_file, "w", encoding="utf-8") as f:
        f.write(f"ORIGINAL ENGLISH:\n{english_text}\n\n")
        f.write(f"GUJARATI TRANSLATION:\n{gujarati_text}")
    
    logger.info(f"Translation saved to {translation_file}")
    
    # For debugging, translate back to English to verify
    back_translation = translator.translate_text(
        gujarati_text, 
        source_lang="gu", 
        target_lang="en"
    )
    logger.info(f"Back translation: {back_translation['translated_text']}")
    
    # Step 3: Initialize TTS and generate speech
    try:
        logger.info("Initializing TTS generator...")
        tts_generator = TTSGenerator()
        
        # Get lecturer reference files
        portraits_dir = Path("portraits")
        portrait_path = portraits_dir / f"{lecturer_name}.png"
        voice_ref_path = portraits_dir / f"{lecturer_name}_voice.wav"
        
        if not portrait_path.exists():
            raise FileNotFoundError(f"Portrait image not found: {portrait_path}")
        
        if not voice_ref_path.exists():
            raise FileNotFoundError(f"Voice reference not found: {voice_ref_path}")
        
        # Generate speech from translated text
        logger.info("Generating Gujarati speech...")
        speech_file = output_path / "gujarati_speech.wav"
        
        # Since TTS might fail for Gujarati, use a fallback approach
        try:
            tts_generator.synthesize_with_cloned_voice(
                text=gujarati_text,
                reference_audio=str(voice_ref_path),
                language="gu",  # Gujarati
                output_path=str(speech_file),
                speed=1.0
            )
        except Exception as e:
            # If Gujarati TTS fails, try with Hindi as fallback
            logger.warning(f"Gujarati TTS failed: {e}")
            logger.info("Trying Hindi TTS as fallback...")
            
            tts_generator.synthesize_with_cloned_voice(
                text=gujarati_text,
                reference_audio=str(voice_ref_path),
                language="hi",  # Hindi as fallback
                output_path=str(speech_file),
                speed=1.0
            )
        
        logger.info(f"Speech generated at {speech_file}")
        
        # Step 4: Generate video
        logger.info("Initializing video synthesizer...")
        video_synthesizer = SadTalkerWrapper()
        
        video_file = output_path / "gujarati_lecture.mp4"
        logger.info("Generating video...")
        
        result = video_synthesizer.generate_video(
            portrait_path=str(portrait_path),
            audio_path=str(speech_file),
            output_path=str(video_file),
            preprocess="full",
            size=512,
            still=True,  # Use still mode for lecture
            use_enhancer=True
        )
        
        logger.info(f"Video generation completed: {video_file}")
        return str(video_file)
        
    except Exception as e:
        logger.error(f"Failed to generate video: {e}")
        raise

def main():
    """Main function to run from command line."""
    parser = argparse.ArgumentParser(description="Generate Gujarati lecture video")
    parser.add_argument(
        "--text", 
        type=str, 
        default="Welcome to our lecture on artificial intelligence. Today we will learn about machine learning algorithms and their applications in education.",
        help="English text to translate to Gujarati"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default="outputs/gujarati_demo",
        help="Output directory for generated files"
    )
    parser.add_argument(
        "--lecturer", 
        type=str, 
        default="sample_lecturer",
        help="Lecturer profile name"
    )
    
    args = parser.parse_args()
    
    try:
        video_path = create_gujarati_lecture_video(
            english_text=args.text,
            output_dir=args.output,
            lecturer_name=args.lecturer
        )
        print(f"✅ Gujarati lecture video created: {video_path}")
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
