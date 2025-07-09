#!/usr/bin/env python
"""
Setup script for the AI Teaser Video Generator application.
"""

import os
import sys
import subprocess
from pathlib import Path
import shutil

def check_python_version():
    """Check if Python version is compatible."""
    required_version = (3, 8)
    current_version = sys.version_info
    
    if current_version < required_version:
        print(f"Error: Python {required_version[0]}.{required_version[1]} or higher is required.")
        print(f"Current version: {current_version[0]}.{current_version[1]}")
        return False
    return True

def check_env_file():
    """Check if .env file exists, create from template if not."""
    env_path = Path('.env')
    template_path = Path('.env.template')
    
    if env_path.exists():
        print("Found existing .env file.")
        return True
    
    if template_path.exists():
        print("Creating .env file from template...")
        shutil.copy(template_path, env_path)
        print("Please edit the .env file with your Azure OpenAI API credentials.")
        return True
    
    print("Error: .env.template file not found. Please create a .env file manually.")
    return False

def install_requirements():
    """Install required packages."""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        return False

def create_output_directory():
    """Create output directory if it doesn't exist."""
    output_dir = Path("output")
    if not output_dir.exists():
        print("Creating output directory...")
        output_dir.mkdir()
    return True

def main():
    """Main setup function."""
    print("Setting up AI Teaser Video Generator...")
    
    if not check_python_version():
        return False
    
    if not check_env_file():
        return False
    
    if not install_requirements():
        return False
    
    if not create_output_directory():
        return False
    
    print("\nSetup complete! You can now run the application with:")
    print("  streamlit run app.py")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
