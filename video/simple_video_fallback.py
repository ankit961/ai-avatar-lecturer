#!/usr/bin/env python3
"""
Simple video fallback that creates a video with static image and audio.
This is used when SadTalker dependencies have conflicts.
"""

import subprocess
import os
import sys
from pathlib import Path

def create_static_video(image_path, audio_path, output_path):
    """
    Create a video with static image and audio using ffmpeg.
    
    Args:
        image_path: Path to the portrait image
        audio_path: Path to the audio file
        output_path: Path for output video
    """
    # Ensure output directory exists
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Build ffmpeg command
    cmd = [
        'ffmpeg', '-y',  # -y to overwrite existing files
        '-loop', '1',    # Loop the image
        '-i', str(image_path),  # Input image
        '-i', str(audio_path),  # Input audio
        '-c:v', 'libx264',      # Video codec
        '-c:a', 'aac',          # Audio codec
        '-b:a', '192k',         # Audio bitrate
        '-r', '25',             # Frame rate
        '-shortest',            # End when shortest input ends
        '-pix_fmt', 'yuv420p',  # Pixel format for compatibility
        str(output_path)
    ]
    
    print(f"Creating video: {image_path} + {audio_path} -> {output_path}")
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"Video created successfully: {output_path}")
        return str(output_path)
    except subprocess.CalledProcessError as e:
        print(f"Error creating video: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        raise
    except FileNotFoundError:
        print("ffmpeg not found. Please install ffmpeg:")
        print("brew install ffmpeg")
        raise

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python simple_video_fallback.py <image_path> <audio_path> <output_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    audio_path = sys.argv[2] 
    output_path = sys.argv[3]
    
    create_static_video(image_path, audio_path, output_path)
