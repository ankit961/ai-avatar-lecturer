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
from pydantic import BaseModel, Field
import uvicorn

# Import our modules
import sys
sys.path.append(str(Path(__file__).parent.parent))

from asr.asr import ASRProcessor
from translate.translate import Translator
from clone.clone import VoiceCloner
from tts.tts import TTSGenerator
from video.synthesize_video import SadTalkerWrapper

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            
            logger.info("Initializing voice cloner...")
            voice_cloner = VoiceCloner(device=device)
            
            logger.info("Initializing TTS generator...")
            tts_generator = TTSGenerator(device=device)
            
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
    request: TextGenerationRequest
):
    """
    Generate lecturer avatar video from text input.
    """
    task_id = f"text_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    # Initialize task
    tasks[task_id] = {
        "status": "started",
        "progress": 0,
        "message": "Processing text input...",
        "created_at": datetime.now(),
        "type": "text"
    }
    
    # Start background task
    background_tasks.add_task(
        process_text_generation,
        task_id,
        request.text,
        request.language,
        request.lecturer_name,
        request.speed
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
    lecturer_name: str = Form(...),
    speed: float = Form(1.0)
):
    """
    Generate lecturer avatar video from audio input.
    """
    # Validate file
    if audio_file.size > CONFIG["max_file_size"]:
        raise HTTPException(status_code=413, detail="File too large")
    
    file_ext = Path(audio_file.filename).suffix.lower()
    if file_ext not in CONFIG["supported_audio_formats"]:
        raise HTTPException(status_code=400, detail="Unsupported audio format")
    
    task_id = f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    # Save uploaded file
    upload_path = CONFIG["upload_dir"] / f"{task_id}{file_ext}"
    with open(upload_path, "wb") as f:
        content = await audio_file.read()
        f.write(content)
    
    # Initialize task
    tasks[task_id] = {
        "status": "started",
        "progress": 0,
        "message": "Processing audio input...",
        "created_at": datetime.now(),
        "type": "audio",
        "audio_path": str(upload_path)
    }
    
    # Start background task
    background_tasks.add_task(
        process_audio_generation,
        task_id,
        str(upload_path),
        language,
        translate_to,
        lecturer_name,
        speed
    )
    
    return GenerationResponse(
        task_id=task_id,
        status="started",
        message="Audio generation task started"
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
    
    for portrait_file in CONFIG["portraits_dir"].glob("*.jpg"):
        lecturer_name = portrait_file.stem
        
        # Check for corresponding voice file
        voice_file = CONFIG["portraits_dir"] / f"{lecturer_name}_voice.wav"
        
        lecturers.append({
            "name": lecturer_name,
            "portrait": str(portrait_file),
            "voice_reference": str(voice_file) if voice_file.exists() else None
        })
    
    return {"lecturers": lecturers}


async def process_text_generation(
    task_id: str,
    text: str,
    language: str,
    lecturer_name: str,
    speed: float
):
    """Background task for text-based generation."""
    try:
        # Update progress
        tasks[task_id].update({"progress": 10, "message": "Preparing text..."})
        
        # Get lecturer files
        portrait_path, voice_ref_path = get_lecturer_files(lecturer_name)
        
        # Update progress
        tasks[task_id].update({"progress": 20, "message": "Generating speech..."})
        
        # Generate speech using TTS with voice cloning
        output_dir = CONFIG["output_dir"] / task_id
        output_dir.mkdir(exist_ok=True)
        
        audio_path = output_dir / "speech.wav"
        tts_generator.synthesize_with_cloned_voice(
            text=text,
            reference_audio=voice_ref_path,
            language=language,
            output_path=audio_path,
            speed=speed
        )
        
        # Update progress
        tasks[task_id].update({"progress": 60, "message": "Generating video..."})
        
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
            "result_url": f"/result/{task_id}"
        })
        
    except Exception as e:
        logger.error(f"Error in text generation task {task_id}: {e}")
        tasks[task_id].update({
            "status": "failed",
            "progress": 0,
            "message": "Generation failed",
            "error": str(e)
        })


async def process_audio_generation(
    task_id: str,
    audio_path: str,
    language: str,
    translate_to: str,
    lecturer_name: str,
    speed: float
):
    """Background task for audio-based generation."""
    try:
        # Update progress
        tasks[task_id].update({"progress": 10, "message": "Transcribing audio..."})
        
        # Transcribe audio
        transcription_result = asr_processor.transcribe_audio(audio_path, language=language)
        transcribed_text = transcription_result["text"]
        
        # Update progress
        tasks[task_id].update({"progress": 30, "message": "Translating text..."})
        
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
        tasks[task_id].update({"progress": 40, "message": "Preparing lecturer assets..."})
        
        # Get lecturer files
        portrait_path, voice_ref_path = get_lecturer_files(lecturer_name)
        
        # Update progress
        tasks[task_id].update({"progress": 50, "message": "Generating cloned speech..."})
        
        # Generate speech with voice cloning
        output_dir = CONFIG["output_dir"] / task_id
        output_dir.mkdir(exist_ok=True)
        
        cloned_audio_path = output_dir / "cloned_speech.wav"
        tts_generator.synthesize_with_cloned_voice(
            text=final_text,
            reference_audio=voice_ref_path,
            language=translate_to,
            output_path=cloned_audio_path,
            speed=speed
        )
        
        # Update progress
        tasks[task_id].update({"progress": 80, "message": "Generating video..."})
        
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
            "final_text": final_text
        })
        
    except Exception as e:
        logger.error(f"Error in audio generation task {task_id}: {e}")
        tasks[task_id].update({
            "status": "failed",
            "progress": 0,
            "message": "Generation failed",
            "error": str(e)
        })
    finally:
        # Clean up uploaded audio file
        try:
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


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
