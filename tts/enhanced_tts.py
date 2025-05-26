#!/usr/bin/env python3
"""
Enhanced TTS module with better support for Indian languages using multiple TTS engines.
Combines Coqui TTS, gTTS, and pyttsx3 for comprehensive language coverage.
"""

import os
import logging
from typing import Dict, List, Optional, Union, Tuple
from pathlib import Path
import tempfile
import time

import torch
import numpy as np
try:
    from TTS.api import TTS
    TTS_AVAILABLE = True
except Exception as e:
    print(f"Warning: TTS not available due to error: {e}")
    TTS = None
    TTS_AVAILABLE = False
import soundfile as sf

# New imports for enhanced TTS
import gtts
import pyttsx3

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedTTSGenerator:
    """Enhanced Text-to-Speech generator with multi-engine support for Indian languages."""
    
    def __init__(self, device: Optional[str] = None):
        """
        Initialize enhanced TTS generator.
        
        Args:
            device: Device to run inference on ('cpu', 'cuda', or None for auto)
        """
        # Auto-detect device if not specified
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        logger.info(f"Initializing Enhanced TTS Generator on device '{self.device}'")
        
        # Initialize different TTS engines
        self._init_coqui_tts()
        self._init_gtts()
        self._init_pyttsx3()
        
        # Define language mappings and preferences
        self._setup_language_mappings()
        
    def _init_coqui_tts(self):
        """Initialize Coqui TTS model."""
        try:
            if not TTS_AVAILABLE:
                logger.warning("Coqui TTS not available due to TTS import failure")
                self.coqui_tts = None
                return
                
            self.coqui_tts = TTS(
                model_name="tts_models/multilingual/multi-dataset/xtts_v2",
                progress_bar=False
            ).to(self.device)
            logger.info("Coqui TTS initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize Coqui TTS: {e}")
            self.coqui_tts = None
    
    def _init_gtts(self):
        """Initialize gTTS (Google Text-to-Speech)."""
        try:
            # Test gTTS availability
            test_gtts = gtts.gTTS(text="test", lang='en')
            self.gtts_available = True
            logger.info("gTTS initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize gTTS: {e}")
            self.gtts_available = False
    
    def _init_pyttsx3(self):
        """Initialize pyttsx3 (offline TTS engine)."""
        try:
            self.pyttsx3_engine = pyttsx3.init()
            voices = self.pyttsx3_engine.getProperty('voices')
            logger.info(f"pyttsx3 initialized with {len(voices)} voices")
            self.pyttsx3_available = True
        except Exception as e:
            logger.warning(f"Failed to initialize pyttsx3: {e}")
            self.pyttsx3_available = False
    
    def _setup_language_mappings(self):
        """Setup language mappings and engine preferences."""
        # gTTS supported languages (relevant Indian languages)
        self.gtts_languages = {
            'en': 'en',
            'hi': 'hi',
            'bn': 'bn',
            'gu': 'gu',
            'kn': 'kn',
            'ml': 'ml',
            'mr': 'mr',
            'ne': 'ne',
            'pa': 'pa',
            'ta': 'ta',
            'te': 'te',
            'ur': 'ur'
        }
        
        # Coqui TTS supported languages
        self.coqui_languages = [
            'en', 'es', 'fr', 'de', 'it', 'pt', 'pl', 'tr', 'ru', 
            'nl', 'cs', 'ar', 'zh-cn', 'hu', 'ko', 'ja', 'hi'
        ]
        
        # Engine preference order for each language
        self.engine_preferences = {
            'hi': ['coqui', 'gtts', 'pyttsx3'],  # Hindi: Best with Coqui
            'gu': ['gtts', 'coqui', 'pyttsx3'],  # Gujarati: Best with gTTS
            'bn': ['gtts', 'coqui', 'pyttsx3'],  # Bengali: Best with gTTS
            'kn': ['gtts', 'coqui', 'pyttsx3'],  # Kannada: Best with gTTS
            'ml': ['gtts', 'coqui', 'pyttsx3'],  # Malayalam: Best with gTTS
            'mr': ['gtts', 'coqui', 'pyttsx3'],  # Marathi: Best with gTTS
            'pa': ['gtts', 'coqui', 'pyttsx3'],  # Punjabi: Best with gTTS
            'ta': ['gtts', 'coqui', 'pyttsx3'],  # Tamil: Best with gTTS
            'te': ['gtts', 'coqui', 'pyttsx3'],  # Telugu: Best with gTTS
            'ur': ['gtts', 'coqui', 'pyttsx3'],  # Urdu: Best with gTTS
            'en': ['coqui', 'gtts', 'pyttsx3'],  # English: Best with Coqui
        }
    
    def get_supported_languages(self) -> List[str]:
        """Get list of all supported languages across all engines."""
        supported = set()
        
        # Add Coqui languages
        if self.coqui_tts:
            supported.update(self.coqui_languages)
        
        # Add gTTS languages
        if self.gtts_available:
            supported.update(self.gtts_languages.keys())
        
        # pyttsx3 generally supports English and some system voices
        if self.pyttsx3_available:
            supported.add('en')
        
        return sorted(list(supported))
    
    def synthesize_with_coqui(
        self,
        text: str,
        language: str = "en",
        speaker_wav: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> str:
        """Synthesize speech using Coqui TTS."""
        if not self.coqui_tts:
            raise RuntimeError("Coqui TTS not available")
        
        if output_path is None:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                output_path = tmp_file.name
        
        tts_kwargs = {
            "text": text,
            "file_path": str(output_path),
            "language": language
        }
        
        if speaker_wav:
            tts_kwargs["speaker_wav"] = str(speaker_wav)
        
        self.coqui_tts.tts_to_file(**tts_kwargs)
        logger.info(f"Coqui TTS synthesis completed: {output_path}")
        return str(output_path)
    
    def synthesize_with_gtts(
        self,
        text: str,
        language: str = "en",
        output_path: Optional[str] = None
    ) -> str:
        """Synthesize speech using gTTS."""
        if not self.gtts_available:
            raise RuntimeError("gTTS not available")
        
        # Map language code to gTTS format
        gtts_lang = self.gtts_languages.get(language, 'en')
        
        if output_path is None:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
                output_path = tmp_file.name
        
        try:
            tts = gtts.gTTS(text=text, lang=gtts_lang, slow=False)
            tts.save(output_path)
            
            # Convert MP3 to WAV if needed
            if output_path.endswith('.wav') and output_path.endswith('.mp3') == False:
                wav_path = output_path
                mp3_path = output_path.replace('.wav', '.mp3')
                tts.save(mp3_path)
                
                # Convert to WAV using ffmpeg
                import subprocess
                result = subprocess.run([
                    'ffmpeg', '-i', mp3_path, '-acodec', 'pcm_s16le', 
                    '-ar', '22050', wav_path, '-y'
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    os.remove(mp3_path)
                    output_path = wav_path
                else:
                    logger.warning("FFmpeg conversion failed, keeping MP3 format")
                    output_path = mp3_path
            
            logger.info(f"gTTS synthesis completed: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"gTTS synthesis failed: {e}")
            raise
    
    def synthesize_with_pyttsx3(
        self,
        text: str,
        language: str = "en",
        output_path: Optional[str] = None
    ) -> str:
        """Synthesize speech using pyttsx3."""
        if not self.pyttsx3_available:
            raise RuntimeError("pyttsx3 not available")
        
        if output_path is None:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                output_path = tmp_file.name
        
        # Configure pyttsx3
        try:
            voices = self.pyttsx3_engine.getProperty('voices')
            
            # Try to find a suitable voice for the language
            if language == 'hi' and len(voices) > 1:
                # Try to use a different voice for Hindi if available
                self.pyttsx3_engine.setProperty('voice', voices[1].id)
            else:
                self.pyttsx3_engine.setProperty('voice', voices[0].id)
            
            # Set speech rate and volume
            self.pyttsx3_engine.setProperty('rate', 150)
            self.pyttsx3_engine.setProperty('volume', 0.9)
            
            # Save to file with error handling
            self.pyttsx3_engine.save_to_file(text, output_path)
            
            # Use a timeout to prevent hanging
            import threading
            import time
            
            def run_engine():
                try:
                    self.pyttsx3_engine.runAndWait()
                except Exception as e:
                    logger.warning(f"pyttsx3 runAndWait error: {e}")
            
            # Run in a separate thread with timeout
            thread = threading.Thread(target=run_engine)
            thread.daemon = True
            thread.start()
            thread.join(timeout=10)  # 10-second timeout
            
            if thread.is_alive():
                logger.warning("pyttsx3 runAndWait timed out")
                # Continue anyway, file might have been created
            
            # Check if file was created
            if os.path.exists(output_path):
                logger.info(f"pyttsx3 synthesis completed: {output_path}")
                return str(output_path)
            else:
                raise Exception("pyttsx3 failed to create audio file")
                
        except Exception as e:
            logger.error(f"pyttsx3 synthesis failed: {e}")
            raise
    
    def synthesize_speech(
        self,
        text: str,
        language: str = "en",
        speaker_wav: Optional[str] = None,
        output_path: Optional[str] = None,
        prefer_engine: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Synthesize speech using the best available engine for the language.
        
        Args:
            text: Text to synthesize
            language: Language code
            speaker_wav: Reference audio for voice cloning (Coqui only)
            output_path: Output file path
            prefer_engine: Preferred engine ('coqui', 'gtts', 'pyttsx3')
        
        Returns:
            Tuple of (output_path, engine_used)
        """
        if not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Determine engine order
        if prefer_engine:
            engines = [prefer_engine] + [e for e in ['coqui', 'gtts', 'pyttsx3'] if e != prefer_engine]
        else:
            engines = self.engine_preferences.get(language, ['coqui', 'gtts', 'pyttsx3'])
        
        last_error = None
        
        for engine in engines:
            try:
                if engine == 'coqui' and self.coqui_tts and language in self.coqui_languages:
                    result = self.synthesize_with_coqui(text, language, speaker_wav, output_path)
                    return result, 'coqui'
                
                elif engine == 'gtts' and self.gtts_available and language in self.gtts_languages:
                    result = self.synthesize_with_gtts(text, language, output_path)
                    return result, 'gtts'
                
                elif engine == 'pyttsx3' and self.pyttsx3_available:
                    result = self.synthesize_with_pyttsx3(text, language, output_path)
                    return result, 'pyttsx3'
                
            except Exception as e:
                logger.warning(f"Engine {engine} failed for language {language}: {e}")
                last_error = e
                continue
        
        # If all engines failed, raise the last error
        if last_error:
            raise last_error
        else:
            raise RuntimeError(f"No suitable TTS engine available for language: {language}")
    
    def get_engine_info(self) -> Dict:
        """Get information about available engines."""
        return {
            "coqui": {
                "available": self.coqui_tts is not None,
                "languages": self.coqui_languages if self.coqui_tts else [],
                "supports_voice_cloning": True
            },
            "gtts": {
                "available": self.gtts_available,
                "languages": list(self.gtts_languages.keys()) if self.gtts_available else [],
                "supports_voice_cloning": False
            },
            "pyttsx3": {
                "available": self.pyttsx3_available,
                "languages": ["en"],
                "supports_voice_cloning": False
            }
        }


def synthesize_text(
    text: str,
    language: str = "en",
    speaker_wav: Optional[str] = None,
    output_path: Optional[str] = None,
    prefer_engine: Optional[str] = None
) -> Tuple[str, str]:
    """
    Convenience function to synthesize speech with enhanced TTS.
    
    Args:
        text: Text to synthesize
        language: Language code
        speaker_wav: Reference audio for voice cloning
        output_path: Output file path
        prefer_engine: Preferred engine
    
    Returns:
        Tuple of (output_path, engine_used)
    """
    tts_generator = EnhancedTTSGenerator()
    return tts_generator.synthesize_speech(
        text=text,
        language=language,
        speaker_wav=speaker_wav,
        output_path=output_path,
        prefer_engine=prefer_engine
    )


if __name__ == "__main__":
    # Test the enhanced TTS generator
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python enhanced_tts.py <text> <language> [output_path] [engine]")
        print("Languages: en, hi, gu, ta, te, mr, bn, kn, ml, pa, ur")
        print("Engines: coqui, gtts, pyttsx3")
        sys.exit(1)
    
    text = sys.argv[1]
    language = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else None
    prefer_engine = sys.argv[4] if len(sys.argv) > 4 else None
    
    try:
        result_path, engine_used = synthesize_text(
            text=text,
            language=language,
            output_path=output_path,
            prefer_engine=prefer_engine
        )
        
        print(f"Speech synthesized successfully!")
        print(f"Engine used: {engine_used}")
        print(f"Output file: {result_path}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
