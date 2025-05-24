"""
ASR (Automatic Speech Recognition) module using OpenAI Whisper.
Converts audio files to text with language detection.
"""

import os
import tempfile
import logging
from typing import Dict, Optional, Union
from pathlib import Path

import whisper
import torch
import librosa
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ASRProcessor:
    """Whisper-based ASR processor for converting audio to text."""
    
    def __init__(self, model_size: str = "base", device: Optional[str] = None):
        """
        Initialize ASR processor.
        
        Args:
            model_size: Whisper model size ('tiny', 'base', 'small', 'medium', 'large')
            device: Device to run inference on ('cpu', 'cuda', or None for auto)
        """
        self.model_size = model_size
        
        # Auto-detect device if not specified
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        logger.info(f"Initializing Whisper model '{model_size}' on device '{self.device}'")
        
        # Load Whisper model
        try:
            self.model = whisper.load_model(model_size, device=self.device)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    def transcribe_audio(
        self, 
        audio_path: Union[str, Path], 
        language: Optional[str] = None,
        task: str = "transcribe"
    ) -> Dict[str, any]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to audio file
            language: Source language code (e.g., 'hi' for Hindi, 'en' for English)
            task: 'transcribe' or 'translate' (translate to English)
            
        Returns:
            Dictionary containing transcription results
        """
        audio_path = Path(audio_path)
        
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        logger.info(f"Transcribing audio: {audio_path}")
        
        try:
            # Transcribe using Whisper
            result = self.model.transcribe(
                str(audio_path),
                language=language,
                task=task,
                verbose=False
            )
            
            # Extract information
            transcription = {
                "text": result["text"].strip(),
                "language": result["language"],
                "segments": result["segments"],
                "audio_path": str(audio_path)
            }
            
            logger.info(f"Transcription completed. Detected language: {result['language']}")
            logger.info(f"Transcribed text: {transcription['text'][:100]}...")
            
            return transcription
            
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            raise
    
    def preprocess_audio(
        self, 
        audio_path: Union[str, Path], 
        target_sr: int = 16000,
        max_duration: Optional[float] = None
    ) -> str:
        """
        Preprocess audio file for better transcription results.
        
        Args:
            audio_path: Path to input audio file
            target_sr: Target sample rate
            max_duration: Maximum duration in seconds (None for no limit)
            
        Returns:
            Path to preprocessed audio file
        """
        audio_path = Path(audio_path)
        
        try:
            # Load audio
            audio, sr = librosa.load(str(audio_path), sr=None)
            logger.info(f"Loaded audio: {len(audio)/sr:.2f}s at {sr}Hz")
            
            # Trim silence
            audio, _ = librosa.effects.trim(audio, top_db=20)
            
            # Limit duration if specified
            if max_duration and len(audio)/sr > max_duration:
                audio = audio[:int(max_duration * sr)]
                logger.info(f"Trimmed audio to {max_duration}s")
            
            # Resample if needed
            if sr != target_sr:
                audio = librosa.resample(audio, orig_sr=sr, target_sr=target_sr)
                logger.info(f"Resampled audio from {sr}Hz to {target_sr}Hz")
            
            # Normalize audio
            audio = audio / np.max(np.abs(audio))
            
            # Save preprocessed audio
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                output_path = tmp_file.name
                
            # Save as WAV
            import soundfile as sf
            sf.write(output_path, audio, target_sr)
            
            logger.info(f"Preprocessed audio saved to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error preprocessing audio: {e}")
            raise
    
    def batch_transcribe(
        self, 
        audio_files: list, 
        language: Optional[str] = None,
        preprocess: bool = True
    ) -> list:
        """
        Transcribe multiple audio files.
        
        Args:
            audio_files: List of audio file paths
            language: Source language code
            preprocess: Whether to preprocess audio files
            
        Returns:
            List of transcription results
        """
        results = []
        
        for audio_file in audio_files:
            try:
                # Preprocess if requested
                if preprocess:
                    processed_audio = self.preprocess_audio(audio_file)
                else:
                    processed_audio = audio_file
                
                # Transcribe
                result = self.transcribe_audio(processed_audio, language=language)
                results.append(result)
                
                # Clean up preprocessed file
                if preprocess and processed_audio != audio_file:
                    os.unlink(processed_audio)
                    
            except Exception as e:
                logger.error(f"Failed to transcribe {audio_file}: {e}")
                results.append({
                    "text": "",
                    "language": "unknown",
                    "segments": [],
                    "audio_path": str(audio_file),
                    "error": str(e)
                })
        
        return results


def transcribe_audio_file(
    audio_path: Union[str, Path], 
    model_size: str = "base",
    language: Optional[str] = None,
    device: Optional[str] = None
) -> Dict[str, any]:
    """
    Convenience function to transcribe a single audio file.
    
    Args:
        audio_path: Path to audio file
        model_size: Whisper model size
        language: Source language code
        device: Device to run on
        
    Returns:
        Transcription result dictionary
    """
    processor = ASRProcessor(model_size=model_size, device=device)
    return processor.transcribe_audio(audio_path, language=language)


if __name__ == "__main__":
    # Test the ASR processor
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python asr.py <audio_file>")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    
    try:
        result = transcribe_audio_file(audio_file)
        print(f"Detected language: {result['language']}")
        print(f"Transcription: {result['text']}")
    except Exception as e:
        print(f"Error: {e}")
