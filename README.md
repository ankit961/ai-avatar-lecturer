# AI Avatar Lecture 🎭📚

An AI-powered video synthesis system that creates realistic talking avatars for educational lectures. Supports multiple input modes including text, audio files, and direct image+audio combinations with advanced lip-sync technology and multi-language support.

## 🌟 Key Features

### 🎬 Video Generation Modes
- **Text-to-Video**: Convert text to talking avatar videos with TTS
- **Audio-to-Video**: Process uploaded audio files to create talking avatars
- **Custom Image Video**: Use your own portrait images with text input
- **Image + Audio Direct**: Direct video generation from image and audio files (no TTS processing)

### 🎙️ Audio & Speech Processing
- **Advanced TTS**: Multiple TTS engines including Coqui TTS and GTTS
- **Voice Cloning**: Clone specific lecturer voices using Coqui TTS embeddings
- **Multi-language Support**: Support for 10+ languages including English, Hindi, Tamil, Gujarati, etc.
- **Automatic Speech Recognition (ASR)**: Process audio inputs using OpenAI Whisper
- **Language Translation**: Automatic translation between supported languages

### 🎭 Video Synthesis & Enhancement
- **SadTalker Integration**: State-of-the-art lip-sync technology for realistic talking heads
- **Face Enhancement**: Optional GFPGAN face enhancement for higher quality output
- **Still Mode**: Generate lip movements only (no head motion) for faster processing
- **Multiple Resolutions**: Support for 256px and 512px video output
- **Batch Processing**: Efficient processing of multiple frames

### 🌐 User Interface & API
- **Modern Web Interface**: Beautiful, responsive web UI with real-time status updates
- **REST API**: Complete FastAPI backend with background task processing
- **Task Management**: Monitor generation progress with unique task IDs
- **File Management**: Automatic cleanup and organized output structure
- **CORS Support**: Cross-origin resource sharing for frontend integration

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Interface │    │   FastAPI       │    │   AI Models     │
│   (Frontend)    │◄──►│   Backend       │◄──►│   (Processing)  │
│     Port :5001  │    │   Port: 5001    │    │   SadTalker     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   File System   │
                    │   (Outputs)     │
                    └─────────────────┘

Processing Pipeline:
┌─────────┐  ┌──────────────┐  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐
│  Input  │─►│ ASR/Language │─►│ Voice Clone │─►│ TTS/Audio    │─►│ Video Sync  │
│ (Text/  │  │ Detection &  │  │ & Speaker   │  │ Generation   │  │ SadTalker   │
│ Audio)  │  │ Translation  │  │ Embedding   │  │ (Coqui/GTTS) │  │ + GFPGAN    │
└─────────┘  └──────────────┘  └─────────────┘  └──────────────┘  └─────────────┘

Components:
├── ASR (OpenAI Whisper) - Speech-to-text processing
├── Translation (Multi-language support) - Text translation between languages  
├── Voice Cloning (Coqui TTS) - Speaker voice adaptation and embedding
├── TTS (Enhanced TTS) - High-quality text-to-speech generation
├── Video Synthesis (SadTalker) - Lip-sync and talking head generation
└── Face Enhancement (GFPGAN) - Optional face quality improvement
```

## 🚀 Quick Start

### Prerequisites

- **macOS** (tested on macOS)
- **Python 3.8+**
- **Python venv** (built-in virtual environment)
- **FFmpeg** for video processing
- **Git** for cloning repositories

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd ai-avatar-lecture
```

2. **Install system dependencies:**
```bash
# Install FFmpeg
brew install ffmpeg
```

3. **Set up Python environment:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install base requirements
pip install -r requirements.txt
```

4. **Set up SadTalker (Critical for video generation):**
```bash
# Navigate to SadTalker directory
cd SadTalker

# Install compatible dependencies
pip install torchvision==0.15.2
pip install basicsr==1.4.2 facexlib==0.3.0 gfpgan==1.3.8 realesrgan==0.3.0

# Download required models (this will take several minutes and ~1.8GB)
cd checkpoints
wget https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/mapping_00109-model.pth.tar
wget https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/mapping_00229-model.pth.tar
wget https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/SadTalker_V0.0.2_256.safetensors
wget https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/SadTalker_V0.0.2_512.safetensors

# Download face enhancement models
cd ../gfpgan/weights
wget https://github.com/xinntao/facexlib/releases/download/v0.1.0/alignment_WFLW_4HG.pth
wget https://github.com/xinntao/facexlib/releases/download/v0.1.0/detection_Resnet50_Final.pth
wget https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth
wget https://github.com/xinntao/facexlib/releases/download/v0.2.2/parsing_parsenet.pth

cd ../../..
```

5. **Test the installation:**
```bash
python test_installation.py
```

### Running the System

1. **Start the backend server:**
```bash
# Activate environment
source venv/bin/activate

# Start the FastAPI server (defaults to port 5001)
cd backend
python app.py

# Or specify a custom port
python app.py --port 9000
```

2. **Access the web interface:**
```
🌐 Open your browser and navigate to: http://localhost:5001/ui
```

The web interface includes four main tabs:
- **📝 Text to Video**: Generate videos from text input with optional custom portraits
- **🎤 Audio to Video**: Process uploaded audio files with ASR and translation  
- **🖼️ Custom Image Video**: Use custom portraits with text input and voice cloning
- **🎬 Image + Audio Direct**: Direct video generation from image and audio files

3. **Alternative: Direct file access:**
```bash
# If you prefer to open the HTML file directly
open web_interface.html
# Note: You'll need to update the API_BASE URL in the HTML if using different ports
```

4. **Docker deployment (optional):**
```bash
# Build and run with Docker
docker-compose up --build
```

## 📖 Usage Guide

### 1. Text-to-Video Generation

Generate talking avatar videos from text input with optional custom portraits and voice cloning.

**Via Web Interface:**
1. Open `http://localhost:5001/ui` in your browser
2. Go to "📝 Text to Video" tab
3. Enter your lecture content in the text area
4. Select language (auto-detect available)
5. Choose lecturer name or use default
6. (Optional) Upload custom portrait image
7. (Optional) Upload voice reference for cloning
8. Adjust speech speed (0.5x - 2.0x)
9. Click "🎬 Generate Video"
10. Monitor progress and download when ready

**Via API:**
```bash
curl -X POST "http://localhost:5001/generate/text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Welcome students! Today we will explore artificial intelligence...",
    "lecturer_name": "prof_ai",
    "language": "en",
    "speed": 1.0
  }'
```

### 2. Audio-to-Video Generation

Process uploaded audio files with automatic speech recognition and translation support.

**Via Web Interface:**
1. Go to "🎤 Audio to Video" tab
2. Upload your audio file (.wav, .mp3, .m4a, .flac)
3. Select source language (auto-detect available)
4. Choose target language for translation
5. Set lecturer name and speech speed
6. (Optional) Upload custom portrait image
7. (Optional) Upload voice reference for cloning
8. Click "🎬 Generate Video"

**Via API:**
```bash
curl -X POST "http://localhost:5001/generate/audio" \
  -F "audio_file=@/path/to/lecture.wav" \
  -F "language=auto" \
  -F "translate_to=en" \
  -F "lecturer_name=prof_audio"
```

### 3. Custom Image Video Generation

Create personalized avatar videos using your own portrait images.

**Via Web Interface:**
1. Go to "🖼️ Custom Image Video" tab
2. Enter the text content
3. Upload portrait image (JPG, PNG - front-facing recommended)
4. Select source and target languages
5. (Optional) Upload voice reference for better cloning
6. Adjust speech speed
7. Click "🎬 Generate Custom Video"

**Via API:**
```bash
curl -X POST "http://localhost:5001/generate/video-with-image" \
  -F "text=Your lecture content here" \
  -F "image_file=@/path/to/portrait.jpg" \
  -F "language=en" \
  -F "translate_to=hi"
```

### 4. Image + Audio Direct Generation (NEW!)

Create talking avatar videos directly from image and audio files without any text-to-speech processing.

**Via Web Interface:**
1. Go to "🎬 Image + Audio Direct" tab
2. Upload portrait image (JPG, PNG)
3. Upload audio file (.wav, .mp3, .m4a, .flac)
4. Set output name/prefix
5. Enable/disable face enhancement
6. Enable/disable still mode (lip movements only)
7. Click "🎬 Generate Direct Video"

**Via API:**
```bash
curl -X POST "http://localhost:5001/generate/image-with-audio" \
  -F "image_file=@/path/to/portrait.jpg" \
  -F "audio_file=@/path/to/audio.wav" \
  -F "lecturer_name=direct_avatar" \
  -F "enhance_face=true" \
  -F "still_mode=true"
```

### 5. Task Status Monitoring

**Via Web Interface:**
- Real-time progress updates appear automatically
- Download links provided when generation completes
- Error messages displayed if processing fails

**Via API:**
```bash
# Check status using task ID returned from generation endpoints
curl "http://localhost:5001/status/{task_id}"

# Response example
{
  "task_id": "text_20250525_123456_789012",
  "status": "completed",
  "progress": 100,
  "message": "Video generation completed successfully",
  "result_url": "/download/text_20250525_123456_789012/final_video.mp4"
}
```

### 3. Custom Lecturer Profiles

Create and manage custom lecturer profiles by organizing files in the `portraits/` directory:

```
portraits/
├── prof_smith/
│   ├── portrait.png          # High-quality front-facing photo
│   └── voice_reference.wav   # 5-10 second voice sample
├── prof_jones/
│   ├── portrait.jpg          # JPG format also supported
│   └── voice_sample.mp3      # Various audio formats supported
└── sample_lecturer/          # Default lecturer included
    ├── portrait.png
    └── voice.wav
```

**Profile Guidelines:**
- **Portrait Images**: Use high-resolution, front-facing photos with clear facial features
- **Voice References**: 5-10 second clear speech samples work best for voice cloning
- **Naming**: Use descriptive folder names (prof_lastname, dr_firstname, etc.)
- **Formats**: PNG/JPG for images, WAV/MP3/M4A for audio

**Using Custom Profiles:**
1. Create folder in `portraits/` directory
2. Add `portrait.png` and `voice_reference.wav` files
3. Reference the folder name in API calls or web interface
4. The system will automatically use custom files when available

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory for custom configuration:

```env
# API Configuration  
API_HOST=0.0.0.0
API_PORT=5001

# Model Paths
SADTALKER_CHECKPOINT_PATH=./SadTalker/checkpoints
SADTALKER_CONFIG_PATH=./SadTalker/src/config

# Output Settings
OUTPUT_DIR=./outputs
UPLOAD_DIR=./uploads
DEBUG_DIR=./debug_test

# Processing Settings
DEFAULT_BATCH_SIZE=1
DEFAULT_VIDEO_SIZE=256
ENABLE_FACE_ENHANCER=true
DEFAULT_STILL_MODE=true

# TTS Settings
DEFAULT_TTS_SPEED=1.0
VOICE_CLONE_ENABLED=true

# ASR Settings
WHISPER_MODEL_SIZE=base
ASR_LANGUAGE_AUTO_DETECT=true
```

### SadTalker Parameters

Fine-tune video generation by modifying parameters in `video/synthesize_video.py`:

- **`size`**: Output resolution (256 or 512) - 256 recommended for speed
- **`enhancer`**: Enable GFPGAN face enhancement (true/false)
- **`still`**: Reduce head movement for static appearance (true/false) 
- **`preprocess`**: Processing mode ('crop', 'resize', 'full')
- **`batch_size`**: Frames processed together (1-4, higher needs more memory)
- **`exp_scale`**: Expression intensity (0.5-2.0, 1.0 default)
- **`pose_style`**: Head pose variation (0-46, 0 for minimal movement)

### Web Interface Configuration

Update API endpoint in `web_interface.html` if using different port:

```javascript
// Line ~563 in web_interface.html
const API_BASE = 'http://localhost:5001';  // Change port if needed
```

### Performance Tuning

**For faster processing:**
```python
# In video/synthesize_video.py
"size": 256,           # Use smaller resolution
"still": True,         # Disable head movement  
"enhancer": False,     # Disable face enhancement
"batch_size": 2,       # Increase if you have enough memory
```

**For higher quality:**
```python
# In video/synthesize_video.py  
"size": 512,           # Use higher resolution
"still": False,        # Enable natural head movement
"enhancer": True,      # Enable GFPGAN face enhancement
"exp_scale": 1.2,      # Increase expression intensity
```

## 📁 Project Structure

```
doctor-avatar/
├── README.md                    # This comprehensive guide
├── requirements.txt             # Python dependencies  
├── docker-compose.yml           # Docker configuration
├── web_interface.html           # Modern web UI (accessible at /ui)
├── start.sh                     # Quick start script
│
├── backend/                     # FastAPI backend server
│   ├── app.py                  # Main application with all endpoints
│   └── __init__.py
│
├── asr/                        # Automatic Speech Recognition
│   ├── asr.py                  # OpenAI Whisper integration
│   └── __init__.py
│
├── translate/                  # Multi-language translation
│   ├── translate.py            # Translation service
│   └── __init__.py
│
├── clone/                      # Voice cloning system
│   ├── clone.py                # Coqui TTS voice cloning
│   └── __init__.py
│
├── tts/                        # Text-to-Speech engines
│   ├── enhanced_tts.py         # Multi-engine TTS (Coqui, GTTS)
│   ├── tts.py                  # Basic TTS functionality
│   └── __init__.py
│
├── video/                      # Video synthesis pipeline
│   ├── synthesize_video.py     # SadTalker integration wrapper
│   ├── simple_video_fallback.py # Fallback video generator
│   └── __init__.py
│
├── SadTalker/                  # Core lip-sync technology
│   ├── inference.py            # Main SadTalker script
│   ├── checkpoints/            # Model files (~1.8GB)
│   │   ├── mapping_00109-model.pth.tar
│   │   ├── mapping_00229-model.pth.tar 
│   │   ├── SadTalker_V0.0.2_256.safetensors
│   │   └── SadTalker_V0.0.2_512.safetensors
│   ├── src/                    # SadTalker source code
│   │   ├── face3d/            # 3D face modeling
│   │   ├── audio2pose/        # Audio-driven pose generation
│   │   ├── audio2exp/         # Audio-driven expression
│   │   └── config/            # Configuration files
│   └── gfpgan/                # Face enhancement models
│       └── weights/           # GFPGAN model weights
│
├── portraits/                  # Lecturer profiles & assets
│   ├── sample_lecturer.png     # Default lecturer portrait
│   ├── sample_lecturer_voice.wav # Default voice reference
│   ├── Ankit Chauhan.png       # Custom lecturer example
│   ├── Ankit Chauhan_voice.mp3 # Custom voice example
│   └── sample_lecturer/        # Organized profile folder
│       ├── portrait.png
│       └── voice.wav
│
├── outputs/                    # Generated videos & audio
│   ├── text_YYYYMMDD_HHMMSS_*/     # Text-to-video outputs
│   ├── audio_YYYYMMDD_HHMMSS_*/    # Audio-to-video outputs  
│   ├── image_audio_YYYYMMDD_*/     # Image+audio direct outputs
│   └── language_tests/             # Multi-language test outputs
│
├── uploads/                    # Temporary file uploads
├── debug_test/                 # Debug outputs and logs
├── logs/                       # Application logs
│
└── tests/                      # Test suite
    ├── manual/                 # Manual test scripts
    │   ├── test_complete_workflow.py
    │   ├── test_lip_sync.py
    │   ├── test_gujarati_components.py
    │   └── test_*.py           # Various feature tests
    ├── integration/            # Integration tests
    ├── unit/                   # Unit tests
    └── conftest.py            # Test configuration
```

### Key Directories Explained

- **`backend/`**: FastAPI server with all API endpoints and business logic
- **`SadTalker/`**: Core technology for lip-sync video generation
- **`portraits/`**: Lecturer profiles with images and voice references  
- **`outputs/`**: Generated videos organized by timestamp and type
- **`tests/manual/`**: Comprehensive test scripts for all features
- **`web_interface.html`**: Modern responsive UI with 4 generation modes

## 🎯 API Reference

### Core Endpoints

All endpoints are available at `http://localhost:5001` when the backend server is running.

#### GET `/ui`
Serve the web interface.
```bash
# Access the web UI
curl http://localhost:5001/ui
# Or open in browser: http://localhost:5001/ui
```

#### GET `/health`
Check system health and component status.
```bash
curl http://localhost:5001/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-05-25T15:00:00",
  "components": {
    "asr": true,
    "translator": false,
    "voice_cloner": true,
    "tts_generator": true,
    "video_synthesizer": true
  }
}
```

#### POST `/generate/text`
Generate video from text input with optional custom portrait and voice.

**Request:** Multipart form data
- `text`: Text content to synthesize (required)
- `language`: Language code (auto, en, hi, gu, etc.)
- `lecturer_name`: Profile name (default: sample_lecturer)
- `speed`: Speech speed (0.5-2.0, default: 1.0)
- `portrait_file`: Custom portrait image (optional)
- `voice_file`: Voice reference for cloning (optional)

**Response:**
```json
{
  "task_id": "text_20250525_123456_789012",
  "status": "processing",
  "message": "Text video generation started"
}
```

#### POST `/generate/audio`
Generate video from uploaded audio file with ASR and translation.

**Request:** Multipart form data
- `audio_file`: Audio file (.wav, .mp3, .m4a, .flac) (required)
- `language`: Source language (auto-detect default)
- `translate_to`: Target language for translation
- `lecturer_name`: Profile name
- `speed`: Playback speed adjustment
- `portrait_file`: Custom portrait (optional)
- `voice_clone_file`: Voice reference (optional)

#### POST `/generate/video-with-image`
Generate video using custom image with text input.

**Request:** Multipart form data
- `text`: Text content (required)
- `image_file`: Portrait image (required)
- `language`: Source language
- `translate_to`: Target language
- `speed`: Speech speed
- `voice_file`: Voice reference (optional)

#### POST `/generate/image-with-audio` ⭐ NEW!
Direct video generation from image and audio files without TTS processing.

**Request:** Multipart form data
- `image_file`: Portrait image (.jpg, .png) (required)
- `audio_file`: Audio file (.wav, .mp3, .m4a, .flac) (required)
- `lecturer_name`: Output name prefix (default: custom_image_audio)
- `enhance_face`: Enable face enhancement (boolean, default: true)
- `still_mode`: Enable still mode - lip sync only (boolean, default: true)

**Example:**
```bash
curl -X POST "http://localhost:5001/generate/image-with-audio" \
  -F "image_file=@portrait.jpg" \
  -F "audio_file=@lecture.wav" \
  -F "lecturer_name=my_avatar" \
  -F "enhance_face=true" \
  -F "still_mode=false"
```

#### GET `/status/{task_id}`
Check generation status and progress.

**Response:**
```json
{
  "task_id": "text_20250525_123456_789012",
  "status": "completed",
  "progress": 100,
  "message": "Video generation completed successfully",
  "result_url": "/download/text_20250525_123456_789012/final_video.mp4",
  "duration": 245.7,
  "file_size": "15.2 MB"
}
```

#### GET `/download/{path:path}`
Download generated video files.

```bash
# Download the generated video
curl -O "http://localhost:5001/download/text_20250525_123456_789012/final_video.mp4"
```

#### GET `/languages`
Get list of supported languages.

**Response:**
```json
{
  "supported_languages": {
    "en": "English",
    "hi": "Hindi", 
    "gu": "Gujarati",
    "ta": "Tamil",
    "te": "Telugu",
    "mr": "Marathi",
    "bn": "Bengali",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "ur": "Urdu"
  }
}
```

### Status Codes & Task States

**Task Status Values:**
- `processing`: Video generation in progress
- `completed`: Video ready for download
- `failed`: Generation failed (check error message)
- `not_found`: Task ID not found

**HTTP Status Codes:**
- `200`: Success
- `202`: Accepted (async task started)
- `400`: Bad request (invalid parameters)
- `404`: Resource not found
- `500`: Internal server error

### Background Task Processing

All video generation endpoints return immediately with a task ID. Use the `/status/{task_id}` endpoint to monitor progress:

```python
import time
import requests

# Start generation
response = requests.post("http://localhost:5001/generate/text", 
                        data={"text": "Hello world", "lecturer_name": "prof"})
task_id = response.json()["task_id"]

# Poll for completion
while True:
    status = requests.get(f"http://localhost:5001/status/{task_id}").json()
    print(f"Progress: {status['progress']}% - {status['message']}")
    
    if status["status"] == "completed":
        video_url = f"http://localhost:5001{status['result_url']}"
        print(f"Video ready: {video_url}")
        break
    elif status["status"] == "failed":
        print(f"Generation failed: {status.get('error', 'Unknown error')}")
        break
        
    time.sleep(2)
```

## 🔍 Troubleshooting

### Common Issues

#### 1. SadTalker Dependencies
**Error:** `ImportError` or package conflicts
```bash
# Solution: Install compatible versions
pip install torchvision==0.15.2
pip install basicsr==1.4.2 facexlib==0.3.0 gfpgan==1.3.8 realesrgan==0.3.0
```

#### 2. Missing Model Files
**Error:** "Model file not found"
```bash
# Solution: Download all required models
cd SadTalker/checkpoints
# Download commands from installation section
```

#### 3. FFmpeg Not Found
**Error:** "ffmpeg command not found"
```bash
# Solution: Install FFmpeg
brew install ffmpeg
```

#### 4. Memory Issues
**Error:** CUDA out of memory or system memory exhausted
```bash
# Solutions:
# 1. Reduce batch size in video/synthesize_video.py
# 2. Use CPU instead of GPU
# 3. Reduce video resolution (use size=256)
# 4. Close other applications
```

#### 5. Long Processing Times
**Issue:** Video generation takes very long
```bash
# Solutions:
# 1. Use GPU if available
# 2. Disable face enhancer
# 3. Use smaller video size (256px)
# 4. Split long audio into segments
```

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check logs in:
- `logs/` directory
- Console output when running backend
- Browser developer console for frontend issues

### Performance Optimization

1. **GPU Usage:** Ensure CUDA is available for faster processing
2. **Model Caching:** Models are loaded once and cached for subsequent requests
3. **Batch Processing:** Increase batch size if you have sufficient memory
4. **Preprocessing:** Choose appropriate preprocessing mode for your use case

## 🧪 Testing

Run the test suite:
```bash
# Basic installation test
python test_installation.py

# Run unit tests
python -m pytest tests/

# Test specific components
python -m pytest tests/test_asr.py
```

### Manual Testing

1. **Test SadTalker directly:**
```bash
cd SadTalker
python3 inference.py \
  --driven_audio ../portraits/sample_lecturer_voice.wav \
  --source_image ../portraits/sample_lecturer.png \
  --enhancer gfpgan
```

2. **Test API endpoints:**
```bash
# Health check
curl http://localhost:8000/health

# Generate simple video
curl -X POST "http://localhost:8000/generate-video" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello students, welcome to today'\''s lecture", "lecturer_name": "sample_lecturer"}'
```

## 📊 Performance Metrics

### Typical Processing Times

| Audio Duration | Processing Time (GPU) | Processing Time (CPU) |
|---------------|----------------------|----------------------|
| 10 seconds    | ~8-12 minutes        | ~20-30 minutes       |
| 30 seconds    | ~25-35 minutes       | ~60-90 minutes       |
| 60 seconds    | ~50-70 minutes       | ~2-3 hours           |

### Resource Usage

- **Memory:** 2-4GB RAM, 2-6GB GPU memory
- **Storage:** ~2GB for models, variable for outputs
- **CPU:** Moderate usage during processing
- **Network:** Models downloaded once (~1.8GB initial)

## 🔒 Security Considerations

1. **File Uploads:** Validate file types and sizes
2. **API Rate Limiting:** Implement rate limiting for production
3. **Input Sanitization:** Sanitize text inputs
4. **File Cleanup:** Temporary files are cleaned up automatically
5. **Access Control:** Add authentication for production deployment

## 🚀 Production Deployment

### Docker Deployment

```bash
# Build production image
docker build -t ai-avatar-lecture .

# Run with docker-compose
docker-compose up -d

# Scale services
docker-compose up --scale backend=3
```

### Environment Setup

1. **Configure reverse proxy** (nginx/Apache)
2. **Set up SSL certificates** for HTTPS
3. **Configure database** for task tracking (optional)
4. **Set up monitoring** and logging
5. **Implement backup strategy** for generated content

### Scaling Considerations

- **Horizontal Scaling:** Multiple backend instances
- **Load Balancing:** Distribute requests across instances
- **Storage:** Shared storage for generated videos
- **Queue System:** Add Redis/Celery for background processing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8

# Run code formatting
black .

# Run linting
flake8 .

# Run tests
pytest
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **SadTalker:** For the amazing talking head generation technology
- **GFPGAN:** For face enhancement capabilities
- **FastAPI:** For the robust web framework
- **OpenAI:** For inspiration on AI-powered applications

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/your-repo/ai-avatar-lecture/issues)
- **Discussions:** [GitHub Discussions](https://github.com/your-repo/ai-avatar-lecture/discussions)
- **Documentation:** This README and inline code documentation

## 🔄 Changelog

### v1.0.0 (2025-05-24)
- ✅ Complete SadTalker integration with working lip sync
- ✅ Fixed dependency conflicts and model downloads
- ✅ Web interface for easy video generation
- ✅ REST API with background task processing
- ✅ Multi-language support via translation
- ✅ Voice cloning capabilities
- ✅ Comprehensive documentation

### Planned Features
- 🔄 Real-time video generation
- 🔄 Advanced emotion control
- 🔄 Multiple avatar styles
- 🔄 Batch processing improvements
- 🔄 Mobile app interface

---

**🎭 Create realistic talking avatars for education with ease! 📚**

For questions, issues, or contributions, please refer to our [GitHub repository](https://github.com/your-repo/ai-avatar-lecture).


