# Voice AI Assistant

A powerful Voice AI application that combines speech-to-text, large language model conversation, and text-to-speech capabilities to create a responsive voice assistant.

## Features

- **Speech Recognition**: Transcribe your voice into text using OpenAI's Whisper ASR
- **Natural Conversation**: Interact with GPT-4 for intelligent and contextual responses
- **High-Quality Voice Synthesis**: Convert text responses to natural speech using ElevenLabs
- **Voice Selection**: Choose from multiple voices for the AI responses
- **Conversation History**: Maintains context across multiple interactions
- **Responsive UI**: Works on both desktop and mobile devices

## Technology Stack

- **Backend**: Python FastAPI
- **Speech-to-Text**: OpenAI Whisper ASR
- **Language Model**: OpenAI GPT-4
- **Text-to-Speech**: ElevenLabs API
- **Frontend**: HTML, CSS, JavaScript
- **Audio Processing**: pydub, soundfile, ffmpeg

## Getting Started

### Prerequisites

- Python 3.9 or higher
- OpenAI API key (for Whisper ASR and GPT-4)
- ElevenLabs API key (for TTS)

### Installation

1. Clone the repository
2. Create a `.env` file with your API keys (based on `.env.example`)
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the application:
   ```
   python run.py
   ```
5. Open your browser and navigate to `http://localhost:8000`

## Usage

1. **Voice Input**: Click "Start Recording" and speak to the assistant. Click "Stop Recording" when finished.
2. **Text Input**: Alternatively, type your message in the text box and click "Send" or press Enter.
3. **Voice Selection**: Choose different voices from the dropdown menu.
4. **Conversation**: View your conversation history and listen to AI responses with the embedded audio player.

## API Endpoints

The application exposes the following API endpoints:

- `POST /api/voice/transcribe`: Transcribe audio files to text
- `POST /api/voice/chat`: Generate GPT-4 response and convert to speech
- `POST /api/voice/text-to-speech`: Convert text to speech
- `GET /api/voice/voices`: Get available voices from ElevenLabs

## Configuration

You can modify the following settings in `app/utils/config.py`:

- Default voice settings
- API endpoints
- File storage locations
- Model parameters

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for Whisper ASR and GPT-4
- ElevenLabs for the text-to-speech API