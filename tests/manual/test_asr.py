"""
Tests for ASR module.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from asr.asr import ASRProcessor, transcribe_audio_file

class TestASRProcessor:
    """Test ASR functionality."""
    
    def test_asr_initialization(self):
        """Test ASR processor initialization."""
        asr = ASRProcessor(model_size="tiny")
        assert asr.model_size == "tiny"
        assert asr.device in ["cpu", "cuda"]
        assert asr.model is not None
    
    def test_transcribe_audio(self, sample_audio_file):
        """Test audio transcription."""
        asr = ASRProcessor(model_size="tiny")
        
        # This will transcribe the sine wave (likely to empty text)
        result = asr.transcribe_audio(sample_audio_file)
        
        assert isinstance(result, dict)
        assert "text" in result
        assert "language" in result
        assert "segments" in result
        assert "audio_path" in result
    
    def test_preprocess_audio(self, sample_audio_file, temp_dir):
        """Test audio preprocessing."""
        asr = ASRProcessor(model_size="tiny")
        
        processed_path = asr.preprocess_audio(sample_audio_file)
        assert Path(processed_path).exists()
        
        # Clean up
        Path(processed_path).unlink()
    
    def test_convenience_function(self, sample_audio_file):
        """Test convenience function."""
        result = transcribe_audio_file(sample_audio_file, model_size="tiny")
        
        assert isinstance(result, dict)
        assert "text" in result
