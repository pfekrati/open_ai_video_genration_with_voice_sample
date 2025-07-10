"""
Video editing utilities for the video generation application.
This module handles video processing and audio integration.
"""

import os
import logging
import tempfile
from typing import Optional
# from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip
from moviepy.editor import *

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def combine_video_and_audio(video_path: str, audio_data: bytes, output_path: str) -> str:
    """
    Combine video and audio into a final video file.
    
    Args:
        video_path: Path to the input video file
        audio_data: Audio data as bytes
        output_path: Path for the output video file
        
    Returns:
        Path to the final video file
    """
    try:
        # Create a temporary file for the audio
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio_file:
            temp_audio_path = temp_audio_file.name
            temp_audio_file.write(audio_data)
        
        logger.info(f"Temporary audio file created at {temp_audio_path}")
        
        # Load the video clip
        video_clip = VideoFileClip(video_path)
        
        # Load the audio clip
        audio_clip = AudioFileClip(temp_audio_path)
        
        # Check if audio is longer than video
        if audio_clip.duration > video_clip.duration:
            logger.warning("Audio duration exceeds video duration. Trimming audio.")
            audio_clip = audio_clip.subclip(0, video_clip.duration)
        
        # Set the audio of the video clip
        final_clip = video_clip.set_audio(audio_clip)
        
        # Write the result to a file
        final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac', fps=24)
        
        # Close the clips to release resources
        video_clip.close()
        audio_clip.close()
        final_clip.close()
        
        # Remove the temporary audio file
        os.unlink(temp_audio_path)
        
        logger.info(f"Successfully created final video at {output_path}")
        
        return output_path
    
    except Exception as e:
        logger.error(f"Error combining video and audio: {str(e)}")
        # Ensure temporary file is removed even if there's an error
        if 'temp_audio_path' in locals() and os.path.exists(temp_audio_path):
            os.unlink(temp_audio_path)
        raise
