# AI Avatar Lecture 🎭📚

An AI-powered video synthesis system that creates realistic talking avatars for educational lectures from text input, supporting multiple languages with voice cloning and lip-sync technology.

## 🌟 Features

- **Text-to-Speech (TTS)**: Convert text to natural speech using advanced TTS models
- **Voice Cloning**: Clone specific lecturer voices for personalized avatars
- **Multi-language Support**: Support for multiple languages via translation
- **Automatic Speech Recognition (ASR)**: Process audio inputs for voice cloning
- **Realistic Lip Sync**: Generate talking head videos with accurate lip synchronization using SadTalker
- **Face Enhancement**: Optional face enhancement for higher quality output
- **Web Interface**: User-friendly web interface for easy interaction
- **REST API**: Complete FastAPI backend for programmatic access
- **Multiple Input Modes**: Support text input, audio upload, and custom lecturer profiles

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Interface │    │   FastAPI       │    │   AI Models     │
│   (Frontend)    │◄──►│   Backend       │◄──►│   (Processing)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   File System   │
                    │   (Outputs)     │
                    └─────────────────┘

Components:
├── ASR (Automatic Speech Recognition)
├── Translation (Multi-language support)
├── Voice Cloning (Speaker adaptation)
├── TTS (Text-to-Speech)
└── Video Synthesis (SadTalker integration)
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

# Start the FastAPI server
cd backend
python app.py
```

2. **Open the web interface:**
```bash
# Open the web interface in your browser
open web_interface.html
# Or manually navigate to the file in your browser
```

3. **Alternative: Use Docker (if available):**
```bash
# Build and run with Docker
docker-compose up --build
```

## 📖 Usage Guide

### 1. Text-to-Video Generation

**Via Web Interface:**
1. Open `web_interface.html` in your browser
2. Go to "Text to Video" tab
3. Enter your lecture content
4. Select or upload a lecturer portrait
5. Choose voice settings (speed, lecturer name)
6. Click "Generate Video"
7. Download the generated video when ready

**Via API:**
```bash
curl -X POST "http://localhost:8000/generate-video" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, I am your AI lecturer. Today we will discuss...",
    "lecturer_name": "sample_lecturer",
    "speed": 1.0
  }'
```

### 2. Audio-to-Video Generation

**Via Web Interface:**
1. Go to "Audio to Video" tab
2. Upload your audio file (.wav, .mp3)
3. Upload or select a portrait image
4. Click "Generate Video"

**Via API:**
```bash
curl -X POST "http://localhost:8000/generate-video-from-audio" \
  -F "audio_file=@/path/to/audio.wav" \
  -F "portrait_file=@/path/to/portrait.png"
```

### 3. Custom Lecturer Profiles

Create custom lecturer profiles by organizing files in the `portraits/` directory:

```
portraits/
├── prof_smith/
│   ├── portrait.png      # Lecturer's photo
│   └── voice_ref.wav     # Voice reference for cloning
└── prof_jones/
    ├── portrait.png
    └── voice_ref.wav
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Model Paths
SADTALKER_CHECKPOINT_PATH=./SadTalker/checkpoints
SADTALKER_CONFIG_PATH=./SadTalker/src/config

# Output Settings
OUTPUT_DIR=./outputs
UPLOAD_DIR=./uploads

# Processing Settings
DEFAULT_BATCH_SIZE=1
DEFAULT_VIDEO_SIZE=256
ENABLE_FACE_ENHANCER=false
```

### SadTalker Parameters

Fine-tune video generation by modifying parameters in `video/synthesize_video.py`:

- **`size`**: Output resolution (256 or 512)
- **`use_enhancer`**: Enable GFPGAN face enhancement
- **`still`**: Reduce head movement for more static appearance
- **`preprocess`**: Processing mode ('crop', 'resize', 'full')
- **`batch_size`**: Number of frames processed together
- **`exp_scale`**: Expression intensity (0.5-2.0)

## 📁 Project Structure

```
ai-avatar-lecture/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── docker-compose.yml        # Docker configuration
├── web_interface.html        # Web UI
├── test_installation.py      # Installation test script
│
├── backend/                  # FastAPI backend
│   ├── app.py               # Main application
│   └── __init__.py
│
├── asr/                     # Speech Recognition
│   ├── asr.py               # ASR processor
│   └── __init__.py
│
├── translate/               # Translation module
│   ├── translate.py         # Language translation
│   └── __init__.py
│
├── clone/                   # Voice cloning
│   ├── clone.py             # Voice cloning logic
│   └── __init__.py
│
├── tts/                     # Text-to-Speech
│   ├── tts.py               # TTS generator
│   └── __init__.py
│
├── video/                   # Video synthesis
│   ├── synthesize_video.py  # SadTalker wrapper
│   ├── simple_video_fallback.py
│   └── __init__.py
│
├── SadTalker/               # SadTalker integration
│   ├── inference.py         # Main SadTalker script
│   ├── checkpoints/         # Model files (~1.8GB)
│   ├── src/                 # Source code
│   └── gfpgan/              # Face enhancement
│
├── portraits/               # Lecturer profiles
│   ├── sample_lecturer.png
│   ├── sample_lecturer_voice.wav
│   └── sample_lecturer/
│
├── outputs/                 # Generated videos
├── uploads/                 # Temporary uploads
└── tests/                   # Test cases
```

## 🎯 API Reference

### Core Endpoints

#### POST `/generate-video`
Generate video from text input.

**Request Body:**
```json
{
  "text": "Your lecture content here",
  "lecturer_name": "sample_lecturer",
  "speed": 1.0,
  "language": "en"
}
```

**Response:**
```json
{
  "task_id": "unique-task-id",
  "status": "processing",
  "message": "Video generation started"
}
```

#### POST `/generate-video-from-audio`
Generate video from audio file.

**Request:** Multipart form data
- `audio_file`: Audio file (.wav, .mp3)
- `portrait_file`: Portrait image (.png, .jpg)

#### GET `/task-status/{task_id}`
Check generation status.

**Response:**
```json
{
  "task_id": "unique-task-id",
  "status": "completed",
  "video_url": "/download/video/filename.mp4",
  "duration": 120.5
}
```

#### GET `/download/video/{filename}`
Download generated video file.

### Status Codes

- `processing`: Video generation in progress
- `completed`: Video ready for download
- `failed`: Generation failed (check logs)
- `not_found`: Task ID not found

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


