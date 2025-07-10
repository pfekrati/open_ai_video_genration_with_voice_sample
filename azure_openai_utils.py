"""
Azure OpenAI utilities for video generation application.
This module handles all interactions with Azure OpenAI services.
"""

import os
import json
import time
import logging
from typing import Dict, Any, Optional
import requests
from openai import AzureOpenAI
from dotenv import load_dotenv
import uuid

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class AzureOpenAIClient:
    """Client for interacting with Azure OpenAI services."""
    
    def __init__(self):
        """Initialize the Azure OpenAI client with configuration from environment variables."""
        # Load configuration from environment variables
        self.api_key = os.getenv("AZURE_OPENAI_KEY")
        self.api_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        self.gpt_deployment_name = os.getenv("GPT_DEPLOYMENT_NAME")
        self.tts_deployment_name = os.getenv("TTS_DEPLOYMENT_NAME")
        self.sora_deployment_name = os.getenv("SORA_DEPLOYMENT_NAME")
        
        # Validate required configuration
        required_vars = [
            self.api_key, self.api_endpoint, self.api_version,
            self.gpt_deployment_name, self.tts_deployment_name, self.sora_deployment_name
        ]
        if not all(required_vars):
            logger.error("Missing required Azure OpenAI configuration (including TTS-specific variables). Please check your .env file.")
            raise ValueError("Missing required Azure OpenAI configuration (including TTS-specific variables)")
        
        # Initialize Azure OpenAI client
        try:
            self.client = AzureOpenAI(
                api_key=self.api_key,
                api_version=self.api_version,
                azure_endpoint=self.api_endpoint
            )
            logger.info("Azure OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI client: {str(e)}")
            raise
    
    def generate_narrative(self, prompt: str, max_tokens: int = 500) -> str:
        """
        Generate a narrative for a video based on the user prompt using GPT-4.1.
        
        Args:
            prompt: User prompt describing the desired video
            max_tokens: Maximum tokens for the completion
            
        Returns:
            Generated narrative text
        """
        try:
            # Create system message for narrative generation
            system_message = """
            You are an expert video script writer. Create a compelling script for voice over video for a 15-second teaser video based on the user's prompt.
            Your narrative should:
            1. Be concise and impactful (approximately 40 words)
            2. Have a clear beginning, middle, and end
            3. Use vivid, descriptive language that can be visually represented
            4. Have a natural flow for narration
            5. Be optimized for less than 15-second duration
            
            Respond with just the narrative text, without any additional commentary.
            """
            
            # Call Azure OpenAI API
            response = self.client.chat.completions.create(
                model=self.gpt_deployment_name,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            narrative = response.choices[0].message.content.strip()
            logger.info(f"Successfully generated narrative of {len(narrative.split())} words")
            return narrative
        
        except Exception as e:
            logger.error(f"Error generating narrative: {str(e)}")
            raise
    
    def generate_tts_instructions(self, narrative: str, max_tokens: int = 300) -> str:
        """
        Generate instructions for text-to-speech delivery based on the narrative.
        
        Args:
            narrative: The narrative text for which to generate TTS instructions
            max_tokens: Maximum tokens for the completion
            
        Returns:
            Instructions for TTS delivery including tone, emphasis, and pacing
        """
        try:
            # Create system message for TTS instruction generation
            system_message = """
            You are an expert voice coach. Create instructions for text-to-speech delivery based on the provided narrative.
            Your instructions should:
            1. Suggest the appropriate tone and emotion for the narration
            2. Indicate where emphasis should be placed
            3. Note where pauses would enhance the delivery
            4. Recommend voice modulation for different parts of the narrative
            5. Be clear and specific to enhance the audio quality
            
            Respond with just the TTS instructions, without any additional commentary.
            """
            
            # Call Azure OpenAI API
            response = self.client.chat.completions.create(
                model=self.gpt_deployment_name,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": narrative}
                ],
                max_tokens=max_tokens,
                temperature=0.6
            )
            
            instructions = response.choices[0].message.content.strip()
            logger.info(f"Successfully generated TTS instructions ({len(instructions.split())} words)")
            return instructions
        
        except Exception as e:
            logger.error(f"Error generating TTS instructions: {str(e)}")
            raise

    def generate_tts(self, text: str, voice: str = "alloy", output_format: str = "mp3") -> bytes:
        """
        Generate high-quality text-to-speech audio using Azure OpenAI TTS HD.
        
        Args:
            text: The narrative text to convert to speech
            voice: The voice to use for TTS (e.g., "alloy", "echo", "fable", "onyx", "nova", "shimmer")
            output_format: The output format of the audio file
            
        Returns:
            Audio data as bytes
        """
        try:
            # Construct the API request to TTS endpoint
            tts_url = f"{self.api_endpoint}/openai/deployments/{self.tts_deployment_name}/audio/speech?api-version=2025-03-01-preview"
            
            headers = {
                "api-key": self.api_key,
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": "gpt-4o-mini-tts",
                "input": text,
                "instructions": self.generate_tts_instructions(text),
                "voice": voice,
                "response_format": output_format
            }
            
            # Make the API request
            response = requests.post(tts_url, headers=headers, json=data)
            
            if response.status_code == 200:
                logger.info(f"Successfully generated TTS audio ({len(response.content)} bytes)")
                return response.content
            else:
                logger.error(f"TTS generation failed with status {response.status_code}: {response.text}")
                raise Exception(f"TTS generation failed: {response.text}")
        
        except Exception as e:
            logger.error(f"Error generating TTS: {str(e)}")
            raise
    
    def generate_sora_instructions(self, narrative: str) -> str:
        """
        Generate detailed instructions for Sora video generation from the narrative.
        
        Args:
            narrative: The narrative text for the video
            
        Returns:
            Detailed instructions for Sora
        """
        try:
            # Create system message for Sora instruction generation
            system_message = """
            You are an expert at creating prompts for AI video generation models like Sora. Convert the provided narrative into detailed 
            instructions that will produce a high-quality 20-second video sequence.
            
            Your instructions should:
            1. Include specific details about visual elements, lighting, and atmosphere
            2. Mention any specific visual styles or references
            3. Be optimized for a 20-second video

            Respond with just the Sora instructions, without any additional commentary.
            """
            
            # Call Azure OpenAI API
            response = self.client.chat.completions.create(
                model=self.gpt_deployment_name,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": narrative}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            instructions = response.choices[0].message.content.strip()
            logger.info(f"Successfully generated Sora instructions ({len(instructions.split())} words)")
            return instructions
        
        except Exception as e:
            logger.error(f"Error generating Sora instructions: {str(e)}")
            raise
    
    def generate_video(self, instructions: str, duration_seconds: int = 20, width: int = 854, height: int = 480, output_path: str = "output") -> str:
        """
        Generate video using Azure OpenAI Sora model.
        
        Args:
            instructions: Detailed instructions for video generation
            duration_seconds: Desired video duration in seconds
            width: Width of the video in pixels
            height: Height of the video in pixels
            output_path: Path where the video should be saved
            
        Returns:
            Path to the generated video file
        """
        try:
            # 1. Create a video generation job
            create_url = f"{self.api_endpoint}/openai/v1/video/generations/jobs?api-version=preview"

            headers = {
                "Api-key": self.api_key,
                "Content-Type": "application/json"
            }
            
            body = {
                "prompt": instructions,
                "width": width,
                "height": height,
                "n_seconds": duration_seconds,
                "n_variants": 1,
                "type": "video_gen",
                "model": "sora"
            }
            
            logger.info("Creating video generation job")
            response = requests.post(create_url, headers=headers, json=body)
            response.raise_for_status()
            
            job_id = response.json()["id"]
            logger.info(f"Job created: {job_id}")
            
            # 2. Poll for job status
            status_url = f"{self.api_endpoint}/openai/v1/video/generations/jobs/{job_id}?api-version=preview"
            status = None
            
            while status not in ("succeeded", "failed", "cancelled"):
                time.sleep(5)  # Wait before polling again
                status_response = requests.get(status_url, headers=headers).json()
                status = status_response.get("status")
                logger.info(f"Job status: {status}")
            
            # 3. Retrieve generated video
            if status == "succeeded":
                generations = status_response.get("generations", [])
                if generations:
                    logger.info("Video generation succeeded")
                    generation_id = generations[0].get("id")
                    video_url = f"{self.api_endpoint}/openai/v1/video/generations/{generation_id}/content/video?api-version=preview"
                    
                    video_response = requests.get(video_url, headers=headers)
                    if video_response.ok:
                        # Generate a random filename with .mp4 extension
                        filename = f"{uuid.uuid4()}.mp4"
                        # Ensure output directory exists
                        os.makedirs(output_path, exist_ok=True)
                        # Combine directory and filename
                        full_path = os.path.join(output_path, filename)
                        
                        with open(full_path, "wb") as file:
                            file.write(video_response.content)
                        logger.info(f'Generated video saved as "{full_path}"')
                        return full_path
                    else:
                        logger.error(f"Failed to download video: {video_response.status_code}")
                        raise Exception(f"Failed to download video: {video_response.text}")
                else:
                    logger.error("No generations found in job result")
                    raise Exception("No generations found in job result")
            else:
                logger.error(f"Job didn't succeed. Status: {status}")
                raise Exception(f"Video generation failed. Status: {status}")
        
        except Exception as e:
            logger.error(f"Error generating video: {str(e)}")
            raise
    
        """
        Download the generated video from the provided URL.
        
        Args:
            video_url: URL of the generated video
            output_path: Path where the video should be saved
            
        Returns:
            Path to the downloaded video file
        """
        try:
            response = requests.get(video_url, stream=True)
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                logger.info(f"Successfully downloaded video to {output_path}")
                return output_path
            else:
                logger.error(f"Video download failed with status {response.status_code}")
                raise Exception(f"Video download failed: {response.status_code}")
        
        except Exception as e:
            logger.error(f"Error downloading video: {str(e)}")
            raise
