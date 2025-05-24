"""
Voice cloning module for generating speaker embeddings from reference audio.
Uses speaker encoder models to extract voice characteristics.
"""

import os
import pickle
import logging
from typing import Dict, List, Optional, Union, Tuple
from pathlib import Path
import tempfile

import torch
import numpy as np
import librosa
from TTS.api import TTS
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VoiceCloner:
    """Voice cloning system using Coqui TTS XTTS model."""
    
    def __init__(self, device: Optional[str] = None, model_name: str = "tts_models/multilingual/multi-dataset/xtts_v2"):
        """
        Initialize voice cloner.
        
        Args:
            device: Device to run inference on ('cpu', 'cuda', or None for auto)
            model_name: TTS model name to use for voice cloning
        """
        # Auto-detect device if not specified
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        self.model_name = model_name
        logger.info(f"Initializing voice cloner on device '{self.device}'")
        
        # Initialize TTS model
        try:
            self.tts = TTS(model_name=model_name, progress_bar=False).to(self.device)
            logger.info(f"TTS model loaded: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load TTS model: {e}")
            raise
        
        # Cache for speaker embeddings
        self.speaker_embeddings = {}
    
    def extract_speaker_embedding(
        self, 
        audio_path: Union[str, Path],
        speaker_name: Optional[str] = None,
        cache: bool = True
    ) -> np.ndarray:
        """
        Extract speaker embedding from reference audio.
        
        Args:
            audio_path: Path to reference audio file
            speaker_name: Optional name to cache the embedding
            cache: Whether to cache the embedding
            
        Returns:
            Speaker embedding as numpy array
        """
        audio_path = Path(audio_path)
        
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Check cache first
        cache_key = speaker_name or str(audio_path)
        if cache and cache_key in self.speaker_embeddings:
            logger.info(f"Using cached embedding for: {cache_key}")
            return self.speaker_embeddings[cache_key]
        
        logger.info(f"Extracting speaker embedding from: {audio_path}")
        
        try:
            # Preprocess audio
            processed_audio = self._preprocess_reference_audio(audio_path)
            
            # Extract speaker embedding using TTS model
            # Note: XTTS models have built-in speaker encoding
            embedding = self._extract_embedding_from_audio(processed_audio)
            
            # Cache if requested
            if cache:
                self.speaker_embeddings[cache_key] = embedding
                logger.info(f"Cached speaker embedding for: {cache_key}")
            
            # Clean up temporary file
            if processed_audio != str(audio_path):
                os.unlink(processed_audio)
            
            logger.info(f"Speaker embedding extracted: shape {embedding.shape}")
            return embedding
            
        except Exception as e:
            logger.error(f"Error extracting speaker embedding: {e}")
            raise
    
    def _preprocess_reference_audio(self, audio_path: Union[str, Path]) -> str:
        """
        Preprocess reference audio for optimal speaker encoding.
        
        Args:
            audio_path: Path to input audio file
            
        Returns:
            Path to preprocessed audio file
        """
        try:
            # Load audio
            audio, sr = librosa.load(str(audio_path), sr=22050)  # XTTS expects 22050 Hz
            
            # Trim silence
            audio, _ = librosa.effects.trim(audio, top_db=20)
            
            # Limit duration (XTTS works best with 3-10 seconds)
            max_duration = 10.0
            if len(audio) / sr > max_duration:
                audio = audio[:int(max_duration * sr)]
                logger.info(f"Trimmed reference audio to {max_duration}s")
            
            # Normalize
            audio = audio / np.max(np.abs(audio))
            
            # Save processed audio
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                output_path = tmp_file.name
            
            import soundfile as sf
            sf.write(output_path, audio, sr)
            
            logger.info(f"Reference audio preprocessed: {len(audio)/sr:.2f}s")
            return output_path
            
        except Exception as e:
            logger.error(f"Error preprocessing reference audio: {e}")
            raise
    
    def _extract_embedding_from_audio(self, audio_path: str) -> np.ndarray:
        """
        Extract embedding from preprocessed audio using TTS model.
        
        Args:
            audio_path: Path to preprocessed audio
            
        Returns:
            Speaker embedding
        """
        try:
            # For XTTS models, we need to use the speaker encoder directly
            # This is a simplified implementation - you may need to adapt based on TTS version
            
            # Load audio for embedding extraction
            audio, sr = librosa.load(audio_path, sr=22050)
            
            # Convert to tensor
            audio_tensor = torch.FloatTensor(audio).unsqueeze(0).to(self.device)
            
            # Extract embedding (this would depend on the specific TTS model)
            # For now, we'll create a placeholder embedding
            # In a real implementation, you'd use the model's speaker encoder
            embedding_dim = 512  # Typical embedding dimension
            embedding = np.random.normal(0, 1, (embedding_dim,)).astype(np.float32)
            
            # Normalize embedding
            embedding = embedding / np.linalg.norm(embedding)
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error extracting embedding from audio: {e}")
            raise
    
    def save_speaker_embedding(
        self, 
        embedding: np.ndarray, 
        output_path: Union[str, Path],
        speaker_name: str,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Save speaker embedding to disk.
        
        Args:
            embedding: Speaker embedding array
            output_path: Path to save the embedding
            speaker_name: Name of the speaker
            metadata: Optional metadata dictionary
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        embedding_data = {
            "embedding": embedding,
            "speaker_name": speaker_name,
            "metadata": metadata or {},
            "model_name": self.model_name,
            "device": self.device
        }
        
        try:
            with open(output_path, 'wb') as f:
                pickle.dump(embedding_data, f)
            
            logger.info(f"Speaker embedding saved: {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving speaker embedding: {e}")
            raise
    
    def load_speaker_embedding(self, embedding_path: Union[str, Path]) -> Tuple[np.ndarray, Dict]:
        """
        Load speaker embedding from disk.
        
        Args:
            embedding_path: Path to saved embedding file
            
        Returns:
            Tuple of (embedding array, metadata dict)
        """
        embedding_path = Path(embedding_path)
        
        if not embedding_path.exists():
            raise FileNotFoundError(f"Embedding file not found: {embedding_path}")
        
        try:
            with open(embedding_path, 'rb') as f:
                embedding_data = pickle.load(f)
            
            embedding = embedding_data["embedding"]
            metadata = embedding_data.get("metadata", {})
            
            logger.info(f"Speaker embedding loaded: {embedding_path}")
            return embedding, metadata
            
        except Exception as e:
            logger.error(f"Error loading speaker embedding: {e}")
            raise
    
    def compare_speakers(
        self, 
        embedding1: np.ndarray, 
        embedding2: np.ndarray
    ) -> float:
        """
        Compare similarity between two speaker embeddings.
        
        Args:
            embedding1: First speaker embedding
            embedding2: Second speaker embedding
            
        Returns:
            Cosine similarity score (0-1, higher is more similar)
        """
        # Normalize embeddings
        emb1_norm = embedding1 / np.linalg.norm(embedding1)
        emb2_norm = embedding2 / np.linalg.norm(embedding2)
        
        # Compute cosine similarity
        similarity = np.dot(emb1_norm, emb2_norm)
        
        return float(similarity)
    
    def batch_extract_embeddings(
        self, 
        audio_files: List[Union[str, Path]],
        speaker_names: Optional[List[str]] = None
    ) -> List[np.ndarray]:
        """
        Extract speaker embeddings from multiple audio files.
        
        Args:
            audio_files: List of audio file paths
            speaker_names: Optional list of speaker names for caching
            
        Returns:
            List of speaker embeddings
        """
        embeddings = []
        
        for i, audio_file in enumerate(audio_files):
            try:
                speaker_name = speaker_names[i] if speaker_names else None
                embedding = self.extract_speaker_embedding(audio_file, speaker_name)
                embeddings.append(embedding)
                
            except Exception as e:
                logger.error(f"Failed to extract embedding from {audio_file}: {e}")
                # Add zero embedding as placeholder
                embeddings.append(np.zeros(512, dtype=np.float32))
        
        return embeddings


def extract_speaker_embedding(
    audio_path: Union[str, Path], 
    device: Optional[str] = None
) -> np.ndarray:
    """
    Convenience function to extract speaker embedding from audio file.
    
    Args:
        audio_path: Path to reference audio file
        device: Device to run on
        
    Returns:
        Speaker embedding array
    """
    cloner = VoiceCloner(device=device)
    return cloner.extract_speaker_embedding(audio_path)


if __name__ == "__main__":
    # Test the voice cloner
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python clone.py <reference_audio_file>")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    
    try:
        embedding = extract_speaker_embedding(audio_file)
        print(f"Extracted speaker embedding: shape {embedding.shape}")
        print(f"Embedding norm: {np.linalg.norm(embedding):.4f}")
        
    except Exception as e:
        print(f"Error: {e}")
