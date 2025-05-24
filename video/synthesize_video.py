"""
Video synthesis module using SadTalker for lip-sync video generation.
Creates talking-head videos from portrait images and audio.
"""

import os
import logging
import subprocess
import shutil
from typing import Dict, List, Optional, Union, Tuple
from pathlib import Path
import tempfile

import torch
import cv2
import numpy as np
from PIL import Image

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SadTalkerWrapper:
    """Wrapper for SadTalker video synthesis."""
    
    def __init__(
        self, 
        sadtalker_path: Optional[Union[str, Path]] = None,
        device: Optional[str] = None,
        checkpoint_dir: Optional[Union[str, Path]] = None
    ):
        """
        Initialize SadTalker wrapper.
        
        Args:
            sadtalker_path: Path to SadTalker repository
            device: Device to run inference on ('cpu', 'cuda', or None for auto)
            checkpoint_dir: Path to SadTalker checkpoints
        """
        # Auto-detect device if not specified
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        # Set SadTalker path
        if sadtalker_path is None:
            # Look for SadTalker in common locations
            self.sadtalker_path = self._find_sadtalker_installation()
        else:
            self.sadtalker_path = Path(sadtalker_path)
        
        # Set checkpoint directory
        if checkpoint_dir is None:
            self.checkpoint_dir = self.sadtalker_path / "checkpoints"
        else:
            self.checkpoint_dir = Path(checkpoint_dir)
        
        logger.info(f"SadTalker path: {self.sadtalker_path}")
        logger.info(f"Checkpoint directory: {self.checkpoint_dir}")
        logger.info(f"Using device: {self.device}")
        
        # Verify installation
        self._verify_installation()
    
    def _find_sadtalker_installation(self) -> Path:
        """Find SadTalker installation automatically."""
        possible_paths = [
            Path.cwd() / "SadTalker",
            Path.home() / "SadTalker",
            Path("/opt/SadTalker"),
            Path("./SadTalker")
        ]
        
        for path in possible_paths:
            if path.exists() and (path / "inference.py").exists():
                return path
        
        # If not found, we'll need to clone it
        logger.warning("SadTalker not found. Will attempt to clone repository.")
        return self._clone_sadtalker()
    
    def _clone_sadtalker(self) -> Path:
        """Clone SadTalker repository."""
        target_dir = Path.cwd() / "SadTalker"
        
        if target_dir.exists():
            return target_dir
        
        logger.info("Cloning SadTalker repository...")
        
        try:
            subprocess.run([
                "git", "clone", 
                "https://github.com/OpenTalker/SadTalker.git",
                str(target_dir)
            ], check=True)
            
            logger.info("SadTalker cloned successfully")
            return target_dir
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to clone SadTalker: {e}")
            raise RuntimeError("Could not clone SadTalker repository")
    
    def _verify_installation(self) -> None:
        """Verify SadTalker installation and download checkpoints if needed."""
        if not self.sadtalker_path.exists():
            raise RuntimeError(f"SadTalker path does not exist: {self.sadtalker_path}")
        
        inference_script = self.sadtalker_path / "inference.py"
        if not inference_script.exists():
            raise RuntimeError(f"SadTalker inference script not found: {inference_script}")
        
        # Check for checkpoints
        if not self.checkpoint_dir.exists():
            logger.info("Checkpoint directory not found. Creating and downloading checkpoints...")
            self._download_checkpoints()
        
        logger.info("SadTalker installation verified")
    
    def _download_checkpoints(self) -> None:
        """Download SadTalker checkpoints."""
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        # This would typically involve downloading model checkpoints
        # For now, we'll create placeholder logic
        logger.info("Checkpoint download would be handled here")
        # In practice, you'd download the actual model files
    
    def generate_video(
        self,
        portrait_path: Union[str, Path],
        audio_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        preprocess: str = "crop",
        still: bool = False,
        use_enhancer: bool = False,
        batch_size: int = 1,
        size: int = 256,
        pose_style: int = 0,
        exp_scale: float = 1.0,
        use_ref_video: bool = False,
        ref_video: Optional[Union[str, Path]] = None,
        ref_info: Optional[str] = None,
        use_idle_mode: bool = False,
        length_of_audio: float = 0,
        use_blink: bool = True
    ) -> str:
        """
        Generate lip-sync video using SadTalker.
        
        Args:
            portrait_path: Path to portrait image
            audio_path: Path to audio file
            output_path: Output video path
            preprocess: Preprocessing method ('crop', 'resize', 'full')
            still: Whether to use still mode
            use_enhancer: Whether to use face enhancer
            batch_size: Batch size for processing
            size: Output video size
            pose_style: Pose style (0-45)
            exp_scale: Expression scale
            use_ref_video: Whether to use reference video
            ref_video: Reference video path
            ref_info: Reference video info
            use_idle_mode: Whether to use idle mode
            length_of_audio: Length of audio
            use_blink: Whether to add blinking
            
        Returns:
            Path to generated video
        """
        portrait_path = Path(portrait_path)
        audio_path = Path(audio_path)
        
        # Verify input files
        if not portrait_path.exists():
            raise FileNotFoundError(f"Portrait image not found: {portrait_path}")
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Create output path if not provided
        if output_path is None:
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_file:
                output_path = Path(tmp_file.name)
        else:
            output_path = Path(output_path)
        
        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Generating video: {portrait_path} + {audio_path} -> {output_path}")
        
        try:
            # Build SadTalker command
            cmd = [
                "python3", str(self.sadtalker_path / "inference.py"),
                "--driven_audio", str(audio_path),
                "--source_image", str(portrait_path),
                "--result_dir", str(output_path.parent),
                "--preprocess", preprocess,
                "--size", str(size),
                "--pose_style", str(pose_style),
                "--expression_scale", str(exp_scale),
                "--batch_size", str(batch_size)
            ]
            
            # Add optional flags
            if still:
                cmd.append("--still")
            if use_enhancer:
                cmd.extend(["--enhancer", "gfpgan"])
            if use_ref_video and ref_video:
                cmd.extend(["--ref_video", str(ref_video)])
            if ref_info:
                cmd.extend(["--ref_info", ref_info])
            if use_idle_mode:
                cmd.append("--use_idle_mode")
            if length_of_audio > 0:
                cmd.extend(["--length_of_audio", str(length_of_audio)])
            if not use_blink:
                cmd.append("--no_blink")
            
            # Set device
            if self.device == "cpu":
                cmd.append("--cpu")
            
            # Run SadTalker
            logger.info(f"Running SadTalker command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                cwd=self.sadtalker_path,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                logger.error(f"SadTalker failed: {result.stderr}")
                raise RuntimeError(f"SadTalker execution failed: {result.stderr}")
            
            # Find generated video file
            # SadTalker typically creates output in a subdirectory
            generated_video = self._find_generated_video(output_path.parent, portrait_path.stem)
            
            if generated_video and generated_video.exists():
                # Move to desired output path
                shutil.move(str(generated_video), str(output_path))
                logger.info(f"Video generated successfully: {output_path}")
                return str(output_path)
            else:
                raise RuntimeError("Generated video file not found")
            
        except Exception as e:
            logger.error(f"Error generating video: {e}")
            raise
    
    def _find_generated_video(self, result_dir: Path, image_stem: str) -> Optional[Path]:
        """Find the generated video file in SadTalker output directory."""
        # SadTalker typically creates nested directories
        for pattern in [
            f"**/{image_stem}*.mp4",
            "**/*.mp4",
            f"{image_stem}*.mp4",
            "*.mp4"
        ]:
            files = list(result_dir.glob(pattern))
            if files:
                # Return the most recently created file
                return max(files, key=lambda p: p.stat().st_mtime)
        
        return None
    
    def preprocess_portrait(
        self,
        image_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        target_size: Tuple[int, int] = (256, 256),
        crop_face: bool = True
    ) -> str:
        """
        Preprocess portrait image for optimal SadTalker results.
        
        Args:
            image_path: Path to input portrait image
            output_path: Output image path
            target_size: Target image size (width, height)
            crop_face: Whether to crop to face region
            
        Returns:
            Path to preprocessed image
        """
        image_path = Path(image_path)
        
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        if output_path is None:
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp_file:
                output_path = tmp_file.name
        
        try:
            # Load image
            image = Image.open(image_path).convert("RGB")
            
            # Resize to target size
            image = image.resize(target_size, Image.Resampling.LANCZOS)
            
            # Save preprocessed image
            image.save(output_path, "JPEG", quality=95)
            
            logger.info(f"Portrait preprocessed: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error preprocessing portrait: {e}")
            raise
    
    def batch_generate_videos(
        self,
        portrait_audio_pairs: List[Tuple[Union[str, Path], Union[str, Path]]],
        output_dir: Union[str, Path],
        **kwargs
    ) -> List[str]:
        """
        Generate multiple videos in batch.
        
        Args:
            portrait_audio_pairs: List of (portrait_path, audio_path) tuples
            output_dir: Output directory for videos
            **kwargs: Additional arguments for generate_video
            
        Returns:
            List of paths to generated videos
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        video_files = []
        
        for i, (portrait_path, audio_path) in enumerate(portrait_audio_pairs):
            try:
                output_path = output_dir / f"video_{i:03d}.mp4"
                
                video_file = self.generate_video(
                    portrait_path=portrait_path,
                    audio_path=audio_path,
                    output_path=output_path,
                    **kwargs
                )
                
                video_files.append(video_file)
                
            except Exception as e:
                logger.error(f"Failed to generate video {i}: {e}")
                video_files.append("")  # Empty path for failed generation
        
        return video_files
    
    def get_video_info(self, video_path: Union[str, Path]) -> Dict:
        """
        Get information about a video file.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with video information
        """
        try:
            cap = cv2.VideoCapture(str(video_path))
            
            if not cap.isOpened():
                raise RuntimeError(f"Could not open video: {video_path}")
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            cap.release()
            
            return {
                "width": width,
                "height": height,
                "fps": fps,
                "frame_count": frame_count,
                "duration": duration,
                "file_size": Path(video_path).stat().st_size
            }
            
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return {}


def generate_talking_head_video(
    portrait_path: Union[str, Path],
    audio_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    sadtalker_path: Optional[Union[str, Path]] = None,
    device: Optional[str] = None,
    **kwargs
) -> str:
    """
    Convenience function to generate talking-head video.
    
    Args:
        portrait_path: Path to portrait image
        audio_path: Path to audio file
        output_path: Output video path
        sadtalker_path: Path to SadTalker installation
        device: Device to run on
        **kwargs: Additional arguments for video generation
        
    Returns:
        Path to generated video
    """
    wrapper = SadTalkerWrapper(sadtalker_path=sadtalker_path, device=device)
    return wrapper.generate_video(
        portrait_path=portrait_path,
        audio_path=audio_path,
        output_path=output_path,
        **kwargs
    )


if __name__ == "__main__":
    # Test the video synthesis
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python synthesize_video.py <portrait_image> <audio_file>")
        sys.exit(1)
    
    portrait_image = sys.argv[1]
    audio_file = sys.argv[2]
    
    try:
        video_file = generate_talking_head_video(
            portrait_path=portrait_image,
            audio_path=audio_file
        )
        
        print(f"Video generated: {video_file}")
        
        # Get video info
        wrapper = SadTalkerWrapper()
        info = wrapper.get_video_info(video_file)
        print(f"Video info: {info}")
        
    except Exception as e:
        print(f"Error: {e}")
