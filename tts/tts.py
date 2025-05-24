"""
TTS (Text-to-Speech) module for generating speech from text with voice cloning.
Uses Coqui TTS with speaker embeddings for voice cloning.
"""

import os
import logging
from typing import Dict, List, Optional, Union, Tuple
from pathlib import Path
import tempfile

import torch
import numpy as np
from TTS.api import TTS
import soundfile as sf

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TTSGenerator:
    """Text-to-Speech generator with voice cloning capabilities."""
    
    def __init__(
        self, 
        device: Optional[str] = None,
        model_name: str = "tts_models/multilingual/multi-dataset/xtts_v2"
    ):
        """
        Initialize TTS generator.
        
        Args:
            device: Device to run inference on ('cpu', 'cuda', or None for auto)
            model_name: TTS model name to use
        """
        # Auto-detect device if not specified
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        self.model_name = model_name
        logger.info(f"Initializing TTS generator on device '{self.device}'")
        
        # Initialize TTS model
        try:
            self.tts = TTS(model_name=model_name, progress_bar=False).to(self.device)
            logger.info(f"TTS model loaded: {model_name}")
            
            # Get supported languages
            self.supported_languages = getattr(self.tts.synthesizer.tts_model, 'language_manager', None)
            if self.supported_languages:
                logger.info(f"Supported languages: {list(self.supported_languages.language_names)}")
                
        except Exception as e:
            logger.error(f"Failed to load TTS model: {e}")
            raise
    
    def synthesize_speech(
        self, 
        text: str,
        speaker_wav: Optional[Union[str, Path]] = None,
        speaker_embedding: Optional[np.ndarray] = None,
        language: str = "en",
        output_path: Optional[Union[str, Path]] = None,
        speed: float = 1.0,
        emotion: Optional[str] = None
    ) -> str:
        """
        Synthesize speech from text with optional voice cloning.
        
        Args:
            text: Text to synthesize
            speaker_wav: Path to reference audio for voice cloning
            speaker_embedding: Pre-computed speaker embedding
            language: Language code ('en', 'hi', etc.)
            output_path: Output audio file path (if None, creates temp file)
            speed: Speech speed multiplier
            emotion: Emotion for synthesis (if supported)
            
        Returns:
            Path to generated audio file
        """
        if not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Create output path if not provided
        if output_path is None:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                output_path = tmp_file.name
        else:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Synthesizing speech: '{text[:50]}...' in language '{language}'")
        
        try:
            # Prepare TTS arguments
            tts_kwargs = {
                "text": text,
                "file_path": str(output_path),
                "language": language,
                "speed": speed
            }
            
            # Add speaker information if provided
            if speaker_wav:
                tts_kwargs["speaker_wav"] = str(speaker_wav)
                logger.info(f"Using speaker reference: {speaker_wav}")
                
            elif speaker_embedding is not None:
                # Note: Direct embedding support depends on TTS model
                # For XTTS, you typically need reference audio
                logger.warning("Direct speaker embedding not fully supported, using default voice")
            
            # Generate speech
            self.tts.tts_to_file(**tts_kwargs)
            
            logger.info(f"Speech synthesized successfully: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error during speech synthesis: {e}")
            raise
    
    def synthesize_with_cloned_voice(
        self,
        text: str,
        reference_audio: Union[str, Path],
        language: str = "en",
        output_path: Optional[Union[str, Path]] = None,
        speed: float = 1.0
    ) -> str:
        """
        Synthesize speech with voice cloning from reference audio.
        
        Args:
            text: Text to synthesize
            reference_audio: Path to reference audio for voice cloning
            language: Language code
            output_path: Output audio file path
            speed: Speech speed multiplier
            
        Returns:
            Path to generated audio file
        """
        reference_audio = Path(reference_audio)
        
        if not reference_audio.exists():
            raise FileNotFoundError(f"Reference audio not found: {reference_audio}")
        
        return self.synthesize_speech(
            text=text,
            speaker_wav=reference_audio,
            language=language,
            output_path=output_path,
            speed=speed
        )
    
    def batch_synthesize(
        self,
        texts: List[str],
        speaker_wav: Optional[Union[str, Path]] = None,
        language: str = "en",
        output_dir: Optional[Union[str, Path]] = None,
        speed: float = 1.0
    ) -> List[str]:
        """
        Synthesize multiple texts in batch.
        
        Args:
            texts: List of texts to synthesize
            speaker_wav: Reference audio for voice cloning
            language: Language code
            output_dir: Output directory for audio files
            speed: Speech speed multiplier
            
        Returns:
            List of paths to generated audio files
        """
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        audio_files = []
        
        for i, text in enumerate(texts):
            try:
                # Create output path
                if output_dir:
                    output_path = output_dir / f"speech_{i:03d}.wav"
                else:
                    output_path = None
                
                # Synthesize
                audio_file = self.synthesize_speech(
                    text=text,
                    speaker_wav=speaker_wav,
                    language=language,
                    output_path=output_path,
                    speed=speed
                )
                
                audio_files.append(audio_file)
                
            except Exception as e:
                logger.error(f"Failed to synthesize text {i}: {e}")
                audio_files.append("")  # Empty path for failed synthesis
        
        return audio_files
    
    def synthesize_segments(
        self,
        segments: List[Dict],
        speaker_wav: Optional[Union[str, Path]] = None,
        language: str = "en",
        output_dir: Optional[Union[str, Path]] = None
    ) -> List[Dict]:
        """
        Synthesize speech from text segments with timing information.
        
        Args:
            segments: List of segment dictionaries with 'text', 'start', 'end'
            speaker_wav: Reference audio for voice cloning
            language: Language code
            output_dir: Output directory for audio files
            
        Returns:
            List of segment dictionaries with added 'audio_path' field
        """
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        processed_segments = []
        
        for i, segment in enumerate(segments):
            try:
                text = segment.get("text", "").strip()
                if not text:
                    continue
                
                # Create output path
                if output_dir:
                    output_path = output_dir / f"segment_{i:03d}.wav"
                else:
                    output_path = None
                
                # Synthesize
                audio_file = self.synthesize_speech(
                    text=text,
                    speaker_wav=speaker_wav,
                    language=language,
                    output_path=output_path
                )
                
                # Create new segment with audio path
                new_segment = segment.copy()
                new_segment["audio_path"] = audio_file
                processed_segments.append(new_segment)
                
            except Exception as e:
                logger.error(f"Failed to synthesize segment {i}: {e}")
                # Keep original segment without audio
                processed_segments.append(segment)
        
        return processed_segments
    
    def get_audio_duration(self, audio_path: Union[str, Path]) -> float:
        """
        Get duration of audio file in seconds.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Duration in seconds
        """
        try:
            info = sf.info(str(audio_path))
            return info.duration
        except Exception as e:
            logger.error(f"Error getting audio duration: {e}")
            return 0.0
    
    def adjust_speech_speed(
        self,
        audio_path: Union[str, Path],
        target_duration: float,
        output_path: Optional[Union[str, Path]] = None
    ) -> str:
        """
        Adjust speech speed to match target duration.
        
        Args:
            audio_path: Path to input audio file
            target_duration: Target duration in seconds
            output_path: Output audio file path
            
        Returns:
            Path to speed-adjusted audio file
        """
        import librosa
        
        audio_path = Path(audio_path)
        
        if output_path is None:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                output_path = tmp_file.name
        
        try:
            # Load audio
            audio, sr = librosa.load(str(audio_path), sr=None)
            current_duration = len(audio) / sr
            
            # Calculate speed factor
            speed_factor = current_duration / target_duration
            
            # Adjust speed using time stretching
            adjusted_audio = librosa.effects.time_stretch(audio, rate=speed_factor)
            
            # Save adjusted audio
            sf.write(str(output_path), adjusted_audio, sr)
            
            logger.info(f"Adjusted speech speed by factor {speed_factor:.2f}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error adjusting speech speed: {e}")
            raise


def synthesize_text(
    text: str,
    speaker_wav: Optional[Union[str, Path]] = None,
    language: str = "en",
    output_path: Optional[Union[str, Path]] = None,
    device: Optional[str] = None
) -> str:
    """
    Convenience function to synthesize speech from text.
    
    Args:
        text: Text to synthesize
        speaker_wav: Reference audio for voice cloning
        language: Language code
        output_path: Output audio file path
        device: Device to run on
        
    Returns:
        Path to generated audio file
    """
    tts_generator = TTSGenerator(device=device)
    return tts_generator.synthesize_speech(
        text=text,
        speaker_wav=speaker_wav,
        language=language,
        output_path=output_path
    )


if __name__ == "__main__":
    # Test the TTS generator
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python tts.py <text> [reference_audio] [language] [output_path]")
        sys.exit(1)
    
    text = sys.argv[1]
    reference_audio = sys.argv[2] if len(sys.argv) > 2 else None
    language = sys.argv[3] if len(sys.argv) > 3 else "en"
    output_path = sys.argv[4] if len(sys.argv) > 4 else None
    
    try:
        audio_file = synthesize_text(
            text=text,
            speaker_wav=reference_audio,
            language=language,
            output_path=output_path
        )
        
        print(f"Speech synthesized: {audio_file}")
        
        # Get duration
        tts_gen = TTSGenerator()
        duration = tts_gen.get_audio_duration(audio_file)
        print(f"Audio duration: {duration:.2f}s")
        
    except Exception as e:
        print(f"Error: {e}")
