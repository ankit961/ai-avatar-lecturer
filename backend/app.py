"""
FastAPI backend for the AI Avatar Lecture system.
Orchestrates ASR, translation, voice cloning, TTS, and video synthesis.
"""

import os
import logging
import tempfile
import asyncio
from typing import Dict, List, Optional, Union
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import uvicorn

# Import our modules
import sys
sys.path.append(str(Path(__file__).parent.parent))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from asr.asr import ASRProcessor
from translate.translate import Translator
try:
    from clone.clone import VoiceCloner
    VOICE_CLONING_AVAILABLE = True
except Exception as e:
    logger.warning(f"Voice cloning not available due to error: {e}")
    VoiceCloner = None
    VOICE_CLONING_AVAILABLE = False

try:
    from tts.enhanced_tts import EnhancedTTSGenerator
    ENHANCED_TTS_AVAILABLE = True
except Exception as e:
    logger.warning(f"Enhanced TTS not available due to error: {e}")
    EnhancedTTSGenerator = None
    ENHANCED_TTS_AVAILABLE = False
from video.synthesize_video import SadTalkerWrapper

# Initialize FastAPI app
app = FastAPI(
    title="AI Avatar Lecture",
    description="AI-powered video synthesis system for creating talking lecturer avatars",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Mount static files directory for testing
# Get application root directory
app_dir = Path(__file__).parent.parent
app.mount("/static", StaticFiles(directory=str(app_dir)), name="static")

# Global components (initialized on startup)
asr_processor = None
translator = None
voice_cloner = None
tts_generator = None
video_synthesizer = None

# Configuration
CONFIG = {
    "upload_dir": Path("uploads"),
    "output_dir": Path("outputs"),
    "portraits_dir": Path("portraits"),
    "max_file_size": 50 * 1024 * 1024,  # 50MB
    "supported_audio_formats": [".wav", ".mp3", ".m4a", ".flac"],
    "supported_image_formats": [".jpg", ".jpeg", ".png"],
    "default_language": "en",
    "device": None  # Auto-detect
}

# Pydantic models
class TextGenerationRequest(BaseModel):
    text: str = Field(..., description="Text to synthesize")
    language: str = Field("en", description="Language code")
    lecturer_name: str = Field(..., description="Lecturer name for voice and portrait")
    speed: float = Field(1.0, description="Speech speed multiplier")


class AudioGenerationRequest(BaseModel):
    language: str = Field("hi", description="Source language of the audio")
    translate_to: str = Field("en", description="Target language for translation")
    lecturer_name: str = Field(..., description="Lecturer name for voice and portrait")
    speed: float = Field(1.0, description="Speech speed multiplier")


class GenerationResponse(BaseModel):
    task_id: str
    status: str
    message: str
    result_url: Optional[str] = None
    error: Optional[str] = None


class StatusResponse(BaseModel):
    task_id: str
    status: str
    progress: int
    message: str
    result_url: Optional[str] = None
    error: Optional[str] = None


# Task storage (in production, use Redis or database)
tasks = {}
task_logs = {}  # Store logs for each task

def log_task_progress(task_id: str, message: str, level: str = "INFO"):
    """Log a message for a specific task and store it."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {"timestamp": timestamp, "level": level, "message": message}
    
    # Initialize list if this is the first log for this task
    if task_id not in task_logs:
        task_logs[task_id] = []
    
    # Add log entry
    task_logs[task_id].append(log_entry)
    
    # Log to main logger as well
    if level == "ERROR":
        logger.error(f"[{task_id}] {message}")
    else:
        logger.info(f"[{task_id}] {message}")


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    global asr_processor, translator, voice_cloner, tts_generator, video_synthesizer
    
    logger.info("Starting AI Avatar Lecture...")
    
    # Create directories
    for dir_path in [CONFIG["upload_dir"], CONFIG["output_dir"], CONFIG["portraits_dir"]]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    logger.info("Server started. Models will be initialized on first use.")


async def initialize_components():
    """Initialize components lazily."""
    global asr_processor, translator, voice_cloner, tts_generator, video_synthesizer
    
    if asr_processor is None:
        logger.info("Initializing components...")
        
        try:
            device = CONFIG["device"]
            
            logger.info("Initializing ASR processor...")
            asr_processor = ASRProcessor(device=device)
            
            logger.info("Initializing translator...")
            translator = Translator(device=device)
            
            if VOICE_CLONING_AVAILABLE:
                logger.info("Initializing voice cloner...")
                voice_cloner = VoiceCloner(device=device)
            else:
                logger.warning("Voice cloning not available, skipping voice_cloner initialization")
                voice_cloner = None
            
            if ENHANCED_TTS_AVAILABLE:
                logger.info("Initializing enhanced TTS generator...")
                tts_generator = EnhancedTTSGenerator(device=device)
            else:
                logger.warning("Enhanced TTS not available, skipping TTS generator initialization")
                tts_generator = None
            
            logger.info("Initializing video synthesizer...")
            video_synthesizer = SadTalkerWrapper(device=device)
            
            logger.info("All components initialized successfully!")
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            raise


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "AI Avatar Lecture API",
        "version": "1.0.0",
        "endpoints": {
            "text_generation": "/generate/text",
            "audio_generation": "/generate/audio",
            "status": "/status/{task_id}",
            "result": "/result/{task_id}",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "asr": asr_processor is not None,
            "translator": translator is not None,
            "voice_cloner": voice_cloner is not None,
            "tts_generator": tts_generator is not None,
            "video_synthesizer": video_synthesizer is not None
        }
    }


@app.get("/languages")
async def get_supported_languages():
    """Get list of supported languages for translation and ASR."""
    # Initialize translator if needed to get language info
    await initialize_components()
    
    indian_languages = {
        "hi": "Hindi",
        "ta": "Tamil", 
        "te": "Telugu",
        "mr": "Marathi",
        "bn": "Bengali",
        "gu": "Gujarati",
        "kn": "Kannada",
        "ml": "Malayalam",
        "pa": "Punjabi",
        "ur": "Urdu"
    }
    
    # Get translator supported languages if available
    translator_languages = indian_languages
    if translator:
        try:
            translator_languages = translator.get_indian_languages()
        except:
            pass
    
    return {
        "supported_languages": translator_languages,
        "default_language": "hi",
        "auto_detect_available": True,
        "translation_info": {
            "all_to_english": "All supported languages can be translated to English",
            "english_to_indian": "English can be translated to most Indian languages",
            "auto_detect": "Automatic language detection available for Indian languages"
        }
    }


@app.post("/generate/text", response_model=GenerationResponse)
async def generate_from_text(
    background_tasks: BackgroundTasks,
    text: str = Form(...),
    language: str = Form("en"),
    lecturer_name: str = Form("sample_lecturer"),
    speed: float = Form(1.0),
    portrait_file: Optional[UploadFile] = File(None),
    voice_file: Optional[UploadFile] = File(None)
):
    """
    Generate lecturer avatar video from text input with optional custom portrait and voice.
    """
    task_id = f"text_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    # Create task output directory
    output_dir = CONFIG["output_dir"] / task_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save uploaded files if provided
    portrait_path = None
    voice_path = None
    
    if portrait_file:
        if portrait_file.size > CONFIG["max_file_size"]:
            raise HTTPException(status_code=413, detail="Portrait file too large")
        
        portrait_ext = Path(portrait_file.filename).suffix.lower()
        if portrait_ext not in CONFIG["supported_image_formats"]:
            raise HTTPException(status_code=400, detail="Unsupported portrait format")
        
        portrait_path = output_dir / f"custom_portrait{portrait_ext}"
        with open(portrait_path, "wb") as f:
            content = await portrait_file.read()
            f.write(content)
    
    if voice_file:
        if voice_file.size > CONFIG["max_file_size"]:
            raise HTTPException(status_code=413, detail="Voice file too large")
        
        voice_ext = Path(voice_file.filename).suffix.lower()
        if voice_ext not in CONFIG["supported_audio_formats"]:
            raise HTTPException(status_code=400, detail="Unsupported voice format")
        
        voice_path = output_dir / f"voice_ref{voice_ext}"
        with open(voice_path, "wb") as f:
            content = await voice_file.read()
            f.write(content)
    
    # Initialize task
    tasks[task_id] = {
        "status": "started",
        "progress": 0,
        "message": "Processing text input...",
        "created_at": datetime.now(),
        "type": "text",
        "portrait_path": str(portrait_path) if portrait_path else None,
        "voice_path": str(voice_path) if voice_path else None
    }
    
    # Start background task
    background_tasks.add_task(
        process_text_generation,
        task_id,
        text,
        language,
        lecturer_name,
        speed,
        str(portrait_path) if portrait_path else None,
        str(voice_path) if voice_path else None
    )
    
    return GenerationResponse(
        task_id=task_id,
        status="started",
        message="Text generation task started"
    )


@app.post("/generate/audio", response_model=GenerationResponse)
async def generate_from_audio(
    background_tasks: BackgroundTasks,
    audio_file: UploadFile = File(...),
    language: str = Form("hi"),
    translate_to: str = Form("en"),
    lecturer_name: str = Form("sample_lecturer"),
    speed: float = Form(1.0),
    portrait_file: Optional[UploadFile] = File(None),
    voice_clone_file: Optional[UploadFile] = File(None)
):
    """
    Generate lecturer avatar video from audio input with optional custom portrait and voice cloning.
    """
    # Validate audio file
    if audio_file.size > CONFIG["max_file_size"]:
        raise HTTPException(status_code=413, detail="Audio file too large")
    
    audio_ext = Path(audio_file.filename).suffix.lower()
    if audio_ext not in CONFIG["supported_audio_formats"]:
        raise HTTPException(status_code=400, detail="Unsupported audio format")
    
    task_id = f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    # Create task output directory
    output_dir = CONFIG["output_dir"] / task_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save uploaded audio file
    audio_path = output_dir / f"input_audio{audio_ext}"
    with open(audio_path, "wb") as f:
        content = await audio_file.read()
        f.write(content)
    
    # Save optional files
    portrait_path = None
    voice_clone_path = None
    
    if portrait_file:
        if portrait_file.size > CONFIG["max_file_size"]:
            raise HTTPException(status_code=413, detail="Portrait file too large")
        
        portrait_ext = Path(portrait_file.filename).suffix.lower()
        if portrait_ext not in CONFIG["supported_image_formats"]:
            raise HTTPException(status_code=400, detail="Unsupported portrait format")
        
        portrait_path = output_dir / f"custom_portrait{portrait_ext}"
        with open(portrait_path, "wb") as f:
            content = await portrait_file.read()
            f.write(content)
    
    if voice_clone_file:
        if voice_clone_file.size > CONFIG["max_file_size"]:
            raise HTTPException(status_code=413, detail="Voice clone file too large")
        
        voice_ext = Path(voice_clone_file.filename).suffix.lower()
        if voice_ext not in CONFIG["supported_audio_formats"]:
            raise HTTPException(status_code=400, detail="Unsupported voice clone format")
        
        voice_clone_path = output_dir / f"voice_clone{voice_ext}"
        with open(voice_clone_path, "wb") as f:
            content = await voice_clone_file.read()
            f.write(content)
    
    # Initialize task
    tasks[task_id] = {
        "status": "started",
        "progress": 0,
        "message": "Processing audio input...",
        "created_at": datetime.now(),
        "type": "audio",
        "audio_path": str(audio_path),
        "portrait_path": str(portrait_path) if portrait_path else None,
        "voice_clone_path": str(voice_clone_path) if voice_clone_path else None
    }
    
    # Start background task
    background_tasks.add_task(
        process_audio_generation,
        task_id,
        str(audio_path),
        language,
        translate_to,
        lecturer_name,
        speed,
        str(portrait_path) if portrait_path else None,
        str(voice_clone_path) if voice_clone_path else None
    )
    
    return GenerationResponse(
        task_id=task_id,
        status="started",
        message="Audio generation task started"
    )


@app.post("/generate/video-with-image", response_model=GenerationResponse)
async def generate_video_with_custom_image(
    background_tasks: BackgroundTasks,
    text: str = Form(...),
    image_file: UploadFile = File(...),
    voice_file: Optional[UploadFile] = File(None),
    language: str = Form("en"),
    translate_to: str = Form("gu"),
    speed: float = Form(1.0)
):
    """
    Generate lecturer avatar video with custom image and optional voice reference.
    """
    # Validate image file
    if image_file.size > CONFIG["max_file_size"]:
        raise HTTPException(status_code=413, detail="Image file too large")
    
    image_ext = Path(image_file.filename).suffix.lower()
    if image_ext not in CONFIG["supported_image_formats"]:
        raise HTTPException(status_code=400, detail="Unsupported image format")
    
    # Validate voice file if provided
    voice_path = None
    if voice_file:
        if voice_file.size > CONFIG["max_file_size"]:
            raise HTTPException(status_code=413, detail="Voice file too large")
        
        voice_ext = Path(voice_file.filename).suffix.lower()
        if voice_ext not in CONFIG["supported_audio_formats"]:
            raise HTTPException(status_code=400, detail="Unsupported voice format")
    
    task_id = f"custom_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    # Create task output directory
    output_dir = CONFIG["output_dir"] / task_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save uploaded image
    image_path = output_dir / f"portrait{image_ext}"
    with open(image_path, "wb") as f:
        content = await image_file.read()
        f.write(content)
    
    # Save uploaded voice file if provided
    if voice_file:
        voice_path = output_dir / f"voice_ref{voice_ext}"
        with open(voice_path, "wb") as f:
            content = await voice_file.read()
            f.write(content)
    
    # Initialize task
    tasks[task_id] = {
        "status": "started",
        "progress": 0,
        "message": "Processing custom image and text...",
        "created_at": datetime.now(),
        "type": "custom_image",
        "image_path": str(image_path),
        "voice_path": str(voice_path) if voice_path else None
    }
    
    # Start background task
    background_tasks.add_task(
        process_custom_image_generation,
        task_id,
        text,
        str(image_path),
        str(voice_path) if voice_path else None,
        language,
        translate_to,
        speed
    )
    
    return GenerationResponse(
        task_id=task_id,
        status="started",
        message="Custom image video generation task started"
    )


@app.post("/generate/image-with-audio", response_model=GenerationResponse)
async def generate_video_from_image_and_audio(
    background_tasks: BackgroundTasks,
    image_file: UploadFile = File(...),
    audio_file: UploadFile = File(...),
    lecturer_name: str = Form("custom_image_audio"),
    enhance_face: bool = Form(True),
    still_mode: bool = Form(True)
):
    """
    Generate video by directly placing audio onto an image (no text-to-speech).
    This creates a talking avatar using the provided image and audio directly.
    """
    # Validate image file
    if image_file.size > CONFIG["max_file_size"]:
        raise HTTPException(status_code=413, detail="Image file too large")
    
    image_ext = Path(image_file.filename).suffix.lower()
    if image_ext not in CONFIG["supported_image_formats"]:
        raise HTTPException(status_code=400, detail="Unsupported image format")
    
    # Validate audio file
    if audio_file.size > CONFIG["max_file_size"]:
        raise HTTPException(status_code=413, detail="Audio file too large")
    
    audio_ext = Path(audio_file.filename).suffix.lower()
    if audio_ext not in CONFIG["supported_audio_formats"]:
        raise HTTPException(status_code=400, detail="Unsupported audio format")
    
    task_id = f"image_audio_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    # Create task output directory
    output_dir = CONFIG["output_dir"] / task_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save uploaded files
    image_path = output_dir / f"input_image{image_ext}"
    audio_path = output_dir / f"input_audio{audio_ext}"
    
    with open(image_path, "wb") as f:
        content = await image_file.read()
        f.write(content)
    
    with open(audio_path, "wb") as f:
        content = await audio_file.read()
        f.write(content)
    
    # Initialize task
    tasks[task_id] = {
        "status": "started",
        "progress": 0,
        "message": "Processing image and audio...",
        "created_at": datetime.now(),
        "type": "image_audio",
        "image_path": str(image_path),
        "audio_path": str(audio_path),
        "lecturer_name": lecturer_name,
        "enhance_face": enhance_face,
        "still_mode": still_mode
    }
    
    # Start background task
    background_tasks.add_task(
        process_image_audio_generation,
        task_id,
        str(image_path),
        str(audio_path),
        lecturer_name,
        enhance_face,
        still_mode
    )
    
    return GenerationResponse(
        task_id=task_id,
        status="started",
        message="Image + Audio video generation started"
    )


@app.get("/status/{task_id}", response_model=StatusResponse)
async def get_task_status(task_id: str):
    """Get status of a generation task."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    
    return StatusResponse(
        task_id=task_id,
        status=task["status"],
        progress=task["progress"],
        message=task["message"],
        result_url=task.get("result_url"),
        error=task.get("error")
    )


@app.get("/result/{task_id}")
async def get_task_result(task_id: str):
    """Download the result video of a completed task."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Task not completed")
    
    result_path = task.get("result_path")
    if not result_path or not Path(result_path).exists():
        raise HTTPException(status_code=404, detail="Result file not found")
    
    return FileResponse(
        result_path,
        media_type="video/mp4",
        filename=f"lecturer_avatar_{task_id}.mp4"
    )


@app.get("/lecturers")
async def list_available_lecturers():
    """List available lecturer portraits and voices."""
    lecturers = []
    
    # Search for all supported image formats
    for ext in CONFIG["supported_image_formats"]:
        for portrait_file in CONFIG["portraits_dir"].glob(f"*{ext}"):
            lecturer_name = portrait_file.stem
            
            # Skip if this lecturer is already added (from another format)
            if any(lecturer["name"] == lecturer_name for lecturer in lecturers):
                continue
            
            # Check for corresponding voice file
            voice_file = None
            for voice_ext in CONFIG["supported_audio_formats"]:
                candidate = CONFIG["portraits_dir"] / f"{lecturer_name}_voice{voice_ext}"
                if candidate.exists():
                    voice_file = candidate
                    break
            
            lecturers.append({
                "name": lecturer_name,
                "portrait": str(portrait_file),
                "voice_reference": str(voice_file) if voice_file else None
            })
    
    return {"lecturers": lecturers}


@app.get("/lecturers/{lecturer_name}")
async def get_lecturer_info(lecturer_name: str):
    """Get detailed information about a specific lecturer."""
    try:
        portrait_path, voice_path = get_lecturer_files(lecturer_name)
        return {
            "name": lecturer_name,
            "exists": True,
            "portrait": portrait_path,
            "voice_reference": voice_path,
            "message": f"Lecturer '{lecturer_name}' is available"
        }
    except FileNotFoundError:
        return {
            "name": lecturer_name,
            "exists": False,
            "portrait": None,
            "voice_reference": None,
            "message": f"Lecturer '{lecturer_name}' not found. Upload both portrait and voice files to create this lecturer.",
            "requirements": {
                "portrait": f"Upload an image file ({', '.join(CONFIG['supported_image_formats'])})",
                "voice": f"Upload an audio file ({', '.join(CONFIG['supported_audio_formats'])})"
            }
        }


# Lecturer management endpoints
@app.post("/lecturers/{lecturer_name}")
async def create_lecturer(
    lecturer_name: str,
    portrait_file: UploadFile = File(...),
    voice_file: UploadFile = File(...)
):
    """Create a new lecturer with portrait and voice files."""
    # Validate files
    if portrait_file.size > CONFIG["max_file_size"]:
        raise HTTPException(status_code=413, detail="Portrait file too large")
    if voice_file.size > CONFIG["max_file_size"]:
        raise HTTPException(status_code=413, detail="Voice file too large")
    
    portrait_ext = Path(portrait_file.filename).suffix.lower()
    voice_ext = Path(voice_file.filename).suffix.lower()
    
    if portrait_ext not in CONFIG["supported_image_formats"]:
        raise HTTPException(status_code=400, detail="Unsupported portrait format")
    if voice_ext not in CONFIG["supported_audio_formats"]:
        raise HTTPException(status_code=400, detail="Unsupported voice format")
    
    # Check if lecturer already exists
    try:
        get_lecturer_files(lecturer_name)
        raise HTTPException(status_code=409, detail=f"Lecturer '{lecturer_name}' already exists")
    except FileNotFoundError:
        pass  # Good, lecturer doesn't exist
    
    # Save files
    portraits_dir = CONFIG["portraits_dir"]
    portrait_path = portraits_dir / f"{lecturer_name}{portrait_ext}"
    voice_path = portraits_dir / f"{lecturer_name}_voice{voice_ext}"
    
    with open(portrait_path, "wb") as f:
        content = await portrait_file.read()
        f.write(content)
    
    with open(voice_path, "wb") as f:
        content = await voice_file.read()
        f.write(content)
    
    logger.info(f"Created new lecturer '{lecturer_name}': portrait={portrait_path}, voice={voice_path}")
    
    return {
        "name": lecturer_name,
        "created": True,
        "portrait": str(portrait_path),
        "voice_reference": str(voice_path),
        "message": f"Lecturer '{lecturer_name}' created successfully"
    }


async def process_text_generation(
    task_id: str,
    text: str,
    language: str,
    lecturer_name: str,
    speed: float,
    custom_portrait_path: Optional[str] = None,
    custom_voice_path: Optional[str] = None
):
    """Background task for text-based generation."""
    try:
        await initialize_components()
        
        # Update progress
        tasks[task_id].update({"progress": 10, "message": "Preparing text..."})
        log_task_progress(task_id, "Preparing text...", "INFO")
        
        # Get lecturer files or create new lecturer
        portrait_path, voice_ref_path = await get_or_create_lecturer_files(
            lecturer_name, 
            custom_portrait_path, 
            custom_voice_path,
            task_id
        )
        
        # Update progress
        tasks[task_id].update({"progress": 20, "message": "Generating speech..."})
        log_task_progress(task_id, "Generating speech...", "INFO")
        
        # Generate speech using TTS with voice cloning
        output_dir = CONFIG["output_dir"] / task_id
        output_dir.mkdir(exist_ok=True)
        
        audio_path = output_dir / "speech.wav"
        result_path, engine_used = tts_generator.synthesize_speech(
            text=text,
            language=language,
            speaker_wav=voice_ref_path,
            output_path=str(audio_path)
        )
        logger.info(f"Speech generated using {engine_used} engine")
        
        # Update progress
        tasks[task_id].update({"progress": 60, "message": "Generating video..."})
        log_task_progress(task_id, "Generating video...", "INFO")
        
        # Generate video
        video_path = output_dir / "avatar_video.mp4"
        video_synthesizer.generate_video(
            portrait_path=portrait_path,
            audio_path=audio_path,
            output_path=video_path
        )
        
        # Update progress
        tasks[task_id].update({
            "status": "completed",
            "progress": 100,
            "message": "Video generation completed",
            "result_path": str(video_path),
            "result_url": f"/result/{task_id}",
            "used_custom_portrait": custom_portrait_path is not None,
            "used_custom_voice": custom_voice_path is not None
        })
        log_task_progress(task_id, "Video generation completed", "INFO")
        
    except Exception as e:
        logger.error(f"Error in text generation task {task_id}: {e}")
        tasks[task_id].update({
            "status": "failed",
            "progress": 0,
            "message": "Generation failed",
            "error": str(e)
        })
        log_task_progress(task_id, f"Generation failed: {e}", "ERROR")


async def process_audio_generation(
    task_id: str,
    audio_path: str,
    language: str,
    translate_to: str,
    lecturer_name: str,
    speed: float,
    custom_portrait_path: Optional[str] = None,
    custom_voice_clone_path: Optional[str] = None
):
    """Background task for audio-based generation with optional custom portrait and voice cloning."""
    try:
        await initialize_components()
        
        # Update progress
        tasks[task_id].update({"progress": 10, "message": "Transcribing audio..."})
        log_task_progress(task_id, "Transcribing audio...", "INFO")
        
        # Transcribe audio
        transcription_result = asr_processor.transcribe_audio(audio_path, language=language)
        transcribed_text = transcription_result["text"]
        
        # Update progress
        tasks[task_id].update({"progress": 30, "message": "Translating text..."})
        log_task_progress(task_id, "Translating text...", "INFO")
        
        # Translate if needed - use smart translation for better Indian language support
        if language != translate_to:
            if language == "auto" or translate_to == "en":
                # Use smart translation for auto-detection or to English
                translation_result = translator.smart_translate(transcribed_text, target_lang=translate_to)
            else:
                # Use specific language pair
                translation_result = translator.translate_text(
                    transcribed_text, 
                    source_lang=language, 
                    target_lang=translate_to
                )
            final_text = translation_result["translated_text"]
            
            # Log translation details
            logger.info(f"Translation: {language} -> {translate_to}")
            logger.info(f"Method: {translation_result.get('translation_method', 'standard')}")
        else:
            final_text = transcribed_text
        
        # Update progress
        tasks[task_id].update({"progress": 40, "message": "Preparing assets..."})
        log_task_progress(task_id, "Preparing assets...", "INFO")
        
        # Get lecturer files or create new lecturer
        portrait_path, voice_ref_path = await get_or_create_lecturer_files(
            lecturer_name, 
            custom_portrait_path, 
            custom_voice_clone_path,
            task_id
        )
        
        # Update progress
        tasks[task_id].update({"progress": 50, "message": "Generating cloned speech..."})
        log_task_progress(task_id, "Generating cloned speech...", "INFO")
        
        # Generate speech with voice cloning
        output_dir = CONFIG["output_dir"] / task_id
        output_dir.mkdir(exist_ok=True)
        
        cloned_audio_path = output_dir / "cloned_speech.wav"
        result_path, engine_used = tts_generator.synthesize_speech(
            text=final_text,
            language=translate_to,
            speaker_wav=voice_ref_path,
            output_path=str(cloned_audio_path)
        )
        logger.info(f"Cloned speech generated using {engine_used} engine")
        
        # Update progress
        tasks[task_id].update({"progress": 80, "message": "Generating video..."})
        log_task_progress(task_id, "Generating video...", "INFO")
        
        # Generate video
        video_path = output_dir / "avatar_video.mp4"
        video_synthesizer.generate_video(
            portrait_path=portrait_path,
            audio_path=cloned_audio_path,
            output_path=video_path
        )
        
        # Update progress
        tasks[task_id].update({
            "status": "completed",
            "progress": 100,
            "message": "Video generation completed",
            "result_path": str(video_path),
            "result_url": f"/result/{task_id}",
            "transcription": transcribed_text,
            "final_text": final_text,
            "used_custom_portrait": custom_portrait_path is not None,
            "used_custom_voice_clone": custom_voice_clone_path is not None
        })
        log_task_progress(task_id, "Video generation completed", "INFO")
        
    except Exception as e:
        logger.error(f"Error in audio generation task {task_id}: {e}")
        tasks[task_id].update({
            "status": "failed",
            "progress": 0,
            "message": "Generation failed",
            "error": str(e)
        })
        log_task_progress(task_id, f"Generation failed: {e}", "ERROR")
    finally:
        # Clean up uploaded audio file
        try:
            Path(audio_path).unlink()
        except:
            pass


async def process_custom_image_generation(
    task_id: str,
    text: str,
    image_path: str,
    voice_path: Optional[str],
    language: str,
    translate_to: str,
    speed: float
):
    """Background task for custom image-based generation."""
    try:
        await initialize_components()
        
        # Update progress
        tasks[task_id].update({"progress": 10, "message": "Processing text..."})
        log_task_progress(task_id, "Processing text...", "INFO")
        
        # Translate text if needed
        final_text = text
        if language != translate_to:
            tasks[task_id].update({"progress": 20, "message": "Translating text..."})
            log_task_progress(task_id, "Translating text...", "INFO")
            
            translation_result = translator.translate_text(
                text, 
                source_lang=language, 
                target_lang=translate_to
            )
            final_text = translation_result["translated_text"]
            
            logger.info(f"Translation: {language} -> {translate_to}")
            logger.info(f"Original: {text}")
            logger.info(f"Translated: {final_text}")
        
        # Update progress
        tasks[task_id].update({"progress": 40, "message": "Generating speech..."})
        log_task_progress(task_id, "Generating speech...", "INFO")
        
        # Generate speech
        output_dir = CONFIG["output_dir"] / task_id
        speech_path = output_dir / "speech.wav"
        
        if voice_path:
            # Use voice cloning with uploaded reference
            result_path, engine_used = tts_generator.synthesize_speech(
                text=final_text,
                language=translate_to,
                speaker_wav=voice_path,
                output_path=str(speech_path)
            )
            logger.info(f"Custom voice speech generated using {engine_used} engine")
        else:
            # Use enhanced TTS for the target language (with automatic engine selection)
            result_path, engine_used = tts_generator.synthesize_speech(
                text=final_text,
                language=translate_to,
                output_path=str(speech_path)
            )
            logger.info(f"Default speech generated using {engine_used} engine")
        
        # Update progress
        tasks[task_id].update({"progress": 70, "message": "Generating video..."})
        log_task_progress(task_id, "Generating video...", "INFO")
        
        # Generate video with custom image
        video_path = output_dir / "custom_avatar_video.mp4"
        video_synthesizer.generate_video(
            portrait_path=image_path,
            audio_path=speech_path,
            output_path=video_path
        )
        
        # Update progress
        tasks[task_id].update({
            "status": "completed",
            "progress": 100,
            "message": "Custom video generation completed",
            "result_path": str(video_path),
            "result_url": f"/result/{task_id}",
            "original_text": text,
            "final_text": final_text,
            "used_voice_cloning": voice_path is not None
        })
        log_task_progress(task_id, "Custom video generation completed", "INFO")
        
    except Exception as e:
        logger.error(f"Error in custom image generation task {task_id}: {e}")
        tasks[task_id].update({
            "status": "failed",
            "progress": 0,
            "message": "Generation failed",
            "error": str(e)
        })
        log_task_progress(task_id, f"Generation failed: {e}", "ERROR")


async def process_image_audio_generation(
    task_id: str,
    image_path: str,
    audio_path: str,
    lecturer_name: str,
    enhance_face: bool,
    still_mode: bool
):
    """
    Background task for image + audio generation (no text-to-speech).
    Directly creates a talking avatar from provided image and audio.
    """
    try:
        await initialize_components()
        
        # Update progress
        tasks[task_id].update({"progress": 10, "message": "Processing image and audio..."})
        log_task_progress(task_id, "Processing image and audio...", "INFO")
        
        # Validate input files exist
        if not Path(image_path).exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        if not Path(audio_path).exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Update progress
        tasks[task_id].update({"progress": 30, "message": "Preparing video generation..."})
        log_task_progress(task_id, "Preparing video generation...", "INFO")
        
        # Get task output directory
        output_dir = CONFIG["output_dir"] / task_id
        output_dir.mkdir(exist_ok=True)
        
        # Update progress
        tasks[task_id].update({"progress": 50, "message": "Generating video with image and audio..."})
        log_task_progress(task_id, "Generating video with image and audio...", "INFO")
        
        # Generate video directly from image and audio
        video_path = output_dir / "image_audio_video.mp4"
        
        # Use the video synthesizer to create the talking head video
        video_synthesizer.generate_video(
            portrait_path=image_path,
            audio_path=audio_path,
            output_path=video_path,
            preprocess='crop' if not still_mode else 'full',
            still=still_mode,
            use_enhancer=enhance_face
        )
        
        # Update progress
        tasks[task_id].update({
            "status": "completed",
            "progress": 100,
            "message": "Image + Audio video generation completed",
            "result_path": str(video_path),
            "result_url": f"/result/{task_id}",
            "lecturer_name": lecturer_name,
            "enhance_face": enhance_face,
            "still_mode": still_mode,
            "image_used": Path(image_path).name,
            "audio_used": Path(audio_path).name
        })
        log_task_progress(task_id, "Image + Audio video generation completed", "INFO")
        
        logger.info(f"Image + Audio video generation completed for task {task_id}")
        
    except Exception as e:
        logger.error(f"Error in image + audio generation task {task_id}: {e}")
        tasks[task_id].update({
            "status": "failed",
            "progress": 0,
            "message": "Generation failed",
            "error": str(e)
        })
        log_task_progress(task_id, f"Generation failed: {e}", "ERROR")
    finally:
        # Clean up uploaded files
        try:
            Path(image_path).unlink()
            Path(audio_path).unlink()
        except:
            pass


def get_lecturer_files(lecturer_name: str) -> tuple:
    """
    Get portrait and voice reference files for a lecturer.
    
    Args:
        lecturer_name: Name of the lecturer
        
    Returns:
        Tuple of (portrait_path, voice_reference_path)
    """
    portraits_dir = CONFIG["portraits_dir"]
    
    # Look for portrait file
    portrait_path = None
    for ext in CONFIG["supported_image_formats"]:
        candidate = portraits_dir / f"{lecturer_name}{ext}"
        if candidate.exists():
            portrait_path = candidate
            break
    
    if not portrait_path:
        raise FileNotFoundError(f"Portrait not found for lecturer: {lecturer_name}")
    
    # Look for voice reference file
    voice_ref_path = None
    for ext in CONFIG["supported_audio_formats"]:
        candidate = portraits_dir / f"{lecturer_name}_voice{ext}"
        if candidate.exists():
            voice_ref_path = candidate
            break
    
    if not voice_ref_path:
        raise FileNotFoundError(f"Voice reference not found for lecturer: {lecturer_name}")
    
    return str(portrait_path), str(voice_ref_path)


async def get_or_create_lecturer_files(
    lecturer_name: str,
    custom_portrait_path: Optional[str] = None,
    custom_voice_path: Optional[str] = None,
    task_id: Optional[str] = None
) -> tuple:
    """
    Get lecturer files or create new lecturer from custom files.
    
    Args:
        lecturer_name: Name of the lecturer
        custom_portrait_path: Path to custom portrait file
        custom_voice_path: Path to custom voice file
        task_id: Task ID for logging
        
    Returns:
        Tuple of (portrait_path, voice_reference_path)
    """
    try:
        # Try to get existing lecturer files first
        return get_lecturer_files(lecturer_name)
    except FileNotFoundError:
        # Lecturer doesn't exist, check if we have custom files to create it
        if custom_portrait_path and custom_voice_path:
            logger.info(f"Creating new lecturer '{lecturer_name}' from uploaded files")
            
            # Create lecturer in portraits directory
            portraits_dir = CONFIG["portraits_dir"]
            
            # Copy custom files to portraits directory with lecturer name
            portrait_ext = Path(custom_portrait_path).suffix
            voice_ext = Path(custom_voice_path).suffix
            
            new_portrait_path = portraits_dir / f"{lecturer_name}{portrait_ext}"
            new_voice_path = portraits_dir / f"{lecturer_name}_voice{voice_ext}"
            
            # Copy files
            import shutil
            shutil.copy2(custom_portrait_path, new_portrait_path)
            shutil.copy2(custom_voice_path, new_voice_path)
            
            logger.info(f"Created new lecturer '{lecturer_name}': portrait={new_portrait_path}, voice={new_voice_path}")
            
            # Update task with lecturer creation info
            if task_id and task_id in tasks:
                tasks[task_id].update({
                    "message": f"Created new lecturer '{lecturer_name}' and generating video...",
                    "created_lecturer": lecturer_name
                })
            
            return str(new_portrait_path), str(new_voice_path)
        
        elif custom_portrait_path or custom_voice_path:
            # Only one file provided, use it and fall back to sample_lecturer for the other
            logger.warning(f"Lecturer '{lecturer_name}' not found. Using provided custom file(s) with sample_lecturer fallback.")
            
            try:
                default_portrait_path, default_voice_ref_path = get_lecturer_files("sample_lecturer")
            except FileNotFoundError:
                raise FileNotFoundError("Neither the requested lecturer nor sample_lecturer is available")
            
            portrait_path = custom_portrait_path or default_portrait_path
            voice_ref_path = custom_voice_path or default_voice_ref_path
            
            # Update task with partial custom info
            if task_id and task_id in tasks:
                custom_files_used = []
                if custom_portrait_path:
                    custom_files_used.append("portrait")
                if custom_voice_path:
                    custom_files_used.append("voice")
                
                tasks[task_id].update({
                    "message": f"Using custom {' and '.join(custom_files_used)} with sample_lecturer fallback...",
                    "partial_custom": True
                })
            
            return portrait_path, voice_ref_path
        
        else:
            # No custom files provided and lecturer doesn't exist
            error_msg = f"Lecturer '{lecturer_name}' not found. Please upload both portrait and voice files to create this lecturer, or use an existing lecturer."
            logger.error(error_msg)
            
            # Update task with helpful error
            if task_id and task_id in tasks:
                tasks[task_id].update({
                    "status": "failed",
                    "progress": 0,
                    "message": "Lecturer not found",
                    "error": error_msg,
                    "suggestion": "Upload both portrait image and voice audio files to create a new lecturer, or choose from available lecturers."
                })
            
            raise FileNotFoundError(error_msg)


# Serve web interface directly
@app.get("/ui", include_in_schema=False)
async def serve_ui():
    """Serve the web interface HTML file."""
    web_interface_path = app_dir / "web_interface.html"
    return FileResponse(web_interface_path)


@app.get("/tasks")
async def list_all_tasks():
    """List all tasks with their current status."""
    task_list = []
    
    for task_id, task_data in tasks.items():
        task_info = {
            "task_id": task_id,
            "status": task_data["status"],
            "progress": task_data["progress"],
            "message": task_data["message"],
            "created_at": task_data.get("created_at", "Unknown"),
            "task_type": task_id.split('_')[0] if '_' in task_id else "unknown",
            "result_url": task_data.get("result_url"),
            "error": task_data.get("error"),
            "used_custom_portrait": task_data.get("used_custom_portrait", False),
            "used_custom_voice": task_data.get("used_custom_voice", False)
        }
        task_list.append(task_info)
    
    # Sort by creation time (newest first)
    task_list.sort(key=lambda x: x["task_id"], reverse=True)
    
    return {
        "total_tasks": len(task_list),
        "tasks": task_list
    }


@app.get("/task_logs/{task_id}")
async def get_task_logs(task_id: str):
    """Get logs for a specific task."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
        
    # Return logs if available, otherwise return empty list
    logs = task_logs.get(task_id, [])
    return {
        "task_id": task_id,
        "logs": logs
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Start the AI Avatar Lecture API server.")
    parser.add_argument("--port", type=int, default=9000, help="Port to run the server on")
    args = parser.parse_args()
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=args.port,
        reload=True,
        log_level="info"
    )
