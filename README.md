# AI Teaser Video Generator

This application uses Azure OpenAI services to create compelling teaser videos based on user prompts. It leverages GPT-4.1 for narrative creation, Azure OpenAI TTS HD for voice generation, and Sora for video generation.

## Features

- Generate engaging 20-second teaser videos from text prompts
- Create high-quality narrative scripts using GPT-4.1
- Convert narratives to natural-sounding speech with OpenAI TTS HD
- Generate video content based on the narrative using Azure OpenAI Sora
- Combine audio and video for a complete teaser experience
- User-friendly web interface built with Streamlit

## Prerequisites

- Azure OpenAI API access with deployments for:
  - GPT-4.1
  - TTS HD
  - Sora
- Python 3.8 or higher

## Installation

1. Clone the repository:
```
git clone [repository-url]
cd open_ai_video_genration_with_voice_sample
```

2. Install the required packages:
```
pip install -r requirements.txt
```

3. Create a `.env` file in the project directory with your Azure OpenAI API credentials:
```
# Azure OpenAI Configuration
AZURE_OPENAI_KEY=your_azure_openai_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# GPT 4.1 Model Deployment Name
GPT_DEPLOYMENT_NAME=your_gpt_deployment_name

# TTS HD Model Configuration
TTS_DEPLOYMENT_NAME=your_tts_deployment_name

# Sora Model Configuration
SORA_DEPLOYMENT_NAME=your_sora_deployment_name
```

## Usage

1. Start the Streamlit application:
```
streamlit run app.py
```

2. Open your web browser and navigate to the URL displayed in the terminal (typically `http://localhost:8501`).

3. Enter a prompt describing the teaser video you want to create.

4. Select a voice for the narration.

5. Click the "Generate Teaser Video" button and wait for the process to complete.

6. Preview and download your generated teaser video.

## Example Prompts

Here are some effective prompts to get you started:

- "Create a teaser for a new adventure film set in the Amazon rainforest featuring ancient ruins and hidden treasures."
- "Generate a product teaser for a revolutionary smart home device that transforms how people interact with their living spaces."
- "Design a teaser for an upcoming documentary about deep-sea exploration and the mysterious creatures that live there."


## Application Structure

- `app.py`: Main application with Streamlit UI
- `azure_openai_utils.py`: Utilities for interacting with Azure OpenAI services
- `video_editor.py`: Functions for video and audio processing
- `requirements.txt`: List of required Python packages
- `output/`: Directory where generated videos are saved

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure your code follows the project's style guidelines and includes appropriate tests.

## Notes

- Video generation may take several minutes depending on the complexity of the request.
- The application uses temporary files that are automatically deleted after use.
- All generated content is stored in the `output` directory with timestamped filenames.

## Security Considerations

- Never share your Azure OpenAI API keys.
- For production use, consider implementing Azure Key Vault for secure credential management.
- Be cautious about the content generated with this tool and ensure it complies with Azure OpenAI content policies.

