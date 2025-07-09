"""
Main application for the AI video generation system.
Uses Streamlit for the web interface.
"""

import os
import time
import logging
import tempfile
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

from azure_openai_utils import AzureOpenAIClient
from video_editor import combine_video_and_audio

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create output directory if it doesn't exist
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

def main():
    st.set_page_config(
        page_title="AI Teaser Video Generator",
        page_icon="🎬",
        layout="wide"
    )
    
    st.title("🎬 AI Teaser Video Generator")
    st.write("""
    Create an engaging 20-second teaser video from just a text prompt!
    This app uses Azure OpenAI services to generate a narrative, convert it to speech, 
    and create a video that matches your vision.
    """)
    
    # Check if Azure OpenAI API keys are configured
    if not os.getenv("AZURE_OPENAI_KEY") or os.getenv("AZURE_OPENAI_KEY") == "your_azure_openai_key_here":
        st.error("""
        **Azure OpenAI API keys not configured!**
        
        Please create a `.env` file in the project directory with the following variables:
        ```
        AZURE_OPENAI_KEY=your_azure_openai_key_here
        AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
        AZURE_OPENAI_API_VERSION=2024-02-15-preview
        GPT_DEPLOYMENT_NAME=your_gpt_deployment_name
        TTS_DEPLOYMENT_NAME=your_tts_deployment_name
        SORA_DEPLOYMENT_NAME=your_sora_deployment_name
        ```
        """)
        return
    
    # Initialize the Azure OpenAI client
    try:
        client = AzureOpenAIClient()
    except Exception as e:
        st.error(f"Failed to initialize Azure OpenAI client: {str(e)}")
        return
    
    # User input for video prompt
    prompt = st.text_area(
        "Describe the teaser video you want to create:",
        "A futuristic city where nature and technology blend seamlessly, with flying vehicles navigating between towering green skyscrapers.",
        height=100
    )
    
    # Voice selection for TTS
    voice_options = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    selected_voice = st.selectbox("Choose a voice for narration:", voice_options)
    
    # Process button
    if st.button("Generate Teaser Video", type="primary"):
        # Create a progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Generate narrative
            status_text.text("Step 1/4: Generating narrative...")
            narrative = client.generate_narrative(prompt)
            progress_bar.progress(25)
            
            # Display the generated narrative
            st.subheader("Generated Narrative")
            st.write(narrative)
            
            # Step 2: Generate speech from narrative
            status_text.text("Step 2/4: Converting narrative to speech...")
            audio_data = client.generate_tts(narrative, voice=selected_voice)
            progress_bar.progress(50)
            
            # Save audio for preview
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
                tmp_audio.write(audio_data)
                audio_path = tmp_audio.name
            
            # Display audio player
            st.subheader("Generated Voice Narration")
            st.audio(audio_path)
            
            # Step 3: Generate Sora instructions
            status_text.text("Step 3/4: Creating video generation instructions...")
            sora_instructions = client.generate_sora_instructions(narrative)
            progress_bar.progress(75)
            
            # Display the generated instructions
            st.subheader("Video Generation Instructions")
            st.write(sora_instructions)
            
            # Step 4: Generate video using Sora
            status_text.text("Step 4/4: Generating video (this may take a while)...")
            video_url = client.generate_video(sora_instructions)
            
            # Create timestamped output file
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            video_path = str(OUTPUT_DIR / f"raw_video_{timestamp}.mp4")
            
            # Download the video
            downloaded_video_path = client.download_video(video_url, video_path)
            
            # Step 5: Combine video and audio
            status_text.text("Finalizing: Combining video and audio...")
            final_video_path = str(OUTPUT_DIR / f"final_video_{timestamp}.mp4")
            final_path = combine_video_and_audio(downloaded_video_path, audio_data, final_video_path)
            progress_bar.progress(100)
            
            # Display the final video
            st.subheader("Your Generated Teaser Video")
            st.video(final_path)
            
            # Success message
            status_text.text("Video generation complete! You can download it using the button below.")
            
            # Download button for the video
            with open(final_path, "rb") as f:
                st.download_button(
                    label="Download Video",
                    data=f,
                    file_name=f"teaser_video_{timestamp}.mp4",
                    mime="video/mp4"
                )
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            logger.error(f"Error in video generation process: {str(e)}")
            status_text.text("Error: Video generation failed. Please try again.")

if __name__ == "__main__":
    main()
