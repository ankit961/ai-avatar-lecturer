"""
Test configuration and fixtures for Doctor Avatar Generator.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import numpy as np
from PIL import Image
import soundfile as sf

@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)

@pytest.fixture
def sample_audio_file(temp_dir):
    """Create a sample audio file for testing."""
    # Generate 1 second of sine wave audio
    sample_rate = 22050
    duration = 1.0
    frequency = 440  # A4 note
    
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio = np.sin(frequency * 2 * np.pi * t) * 0.3
    
    audio_path = temp_dir / "sample_audio.wav"
    sf.write(str(audio_path), audio, sample_rate)
    
    return str(audio_path)

@pytest.fixture
def sample_image_file(temp_dir):
    """Create a sample portrait image for testing."""
    # Create a simple RGB image
    image = Image.new('RGB', (256, 256), color='lightblue')
    
    image_path = temp_dir / "sample_portrait.jpg"
    image.save(str(image_path), "JPEG")
    
    return str(image_path)

@pytest.fixture
def sample_text():
    """Sample text for testing."""
    return "Hello, this is a test message for the doctor avatar generator."

@pytest.fixture
def sample_hindi_text():
    """Sample Hindi text for testing."""
    return "नमस्ते, यह डॉक्टर अवतार जेनरेटर के लिए एक परीक्षण संदेश है।"
