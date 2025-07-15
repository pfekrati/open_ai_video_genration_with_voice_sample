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

def combine_video_and_audio(video_path: str, audio_data: bytes, output_path: str, background_music_path: Optional[str] = None, music_volume: float = 0.3) -> str:
    """
    Combine video, voice narration, and optional background music into a final video file.
    
    Args:
        video_path: Path to the input video file
        audio_data: Voice narration audio data as bytes
        output_path: Path for the output video file
        background_music_path: Optional path to a background music file
        music_volume: Volume level for background music (0.0 to 1.0)
        
    Returns:
        Path to the final video file
    """
    try:
        # Create a temporary file for the voice narration
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio_file:
            temp_audio_path = temp_audio_file.name
            temp_audio_file.write(audio_data)
        
        logger.info(f"Temporary audio file created at {temp_audio_path}")
        
        # Load the video clip
        video_clip = VideoFileClip(video_path)
        
        # Load the voice narration clip
        voice_clip = AudioFileClip(temp_audio_path)
        
        # Check if voice narration is longer than video
        if voice_clip.duration > video_clip.duration:
            logger.warning("Voice narration duration exceeds video duration. Trimming audio.")
            voice_clip = voice_clip.subclip(0, video_clip.duration)
        
        if background_music_path and os.path.exists(background_music_path):
            logger.info(f"Adding background music from {background_music_path}")
            
            # Load the background music
            music_clip = AudioFileClip(background_music_path)
            
            # Loop the music if it's shorter than the video
            if music_clip.duration < video_clip.duration:
                logger.info("Background music is shorter than video. Looping music.")
                repetitions = int(video_clip.duration / music_clip.duration) + 1
                music_clip = concatenate_audioclips([music_clip] * repetitions)
            
            # Trim music if it's longer than the video
            if music_clip.duration > video_clip.duration:
                music_clip = music_clip.subclip(0, video_clip.duration)
            
            # Set the volume of the background music to be lower
            music_clip = music_clip.volumex(music_volume)
            
            # Combine voice narration and background music
            combined_audio = CompositeAudioClip([voice_clip, music_clip])
            
            # Set the combined audio to the video clip
            final_clip = video_clip.set_audio(combined_audio)
        else:
            # Set only the voice narration to the video clip
            final_clip = video_clip.set_audio(voice_clip)
        
        # Write the result to a file
        final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac', fps=24)
        
        # Close the clips to release resources
        video_clip.close()
        voice_clip.close()
        final_clip.close()
        if background_music_path and 'music_clip' in locals():
            music_clip.close()
        
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
