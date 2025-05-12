import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI API configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY environment variable not set")

# ElevenLabs API configuration
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    print("Warning: ELEVENLABS_API_KEY environment variable not set")

# Default voice ID for ElevenLabs (Rachel)
DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"

# Audio directories
UPLOADS_DIR = "app/static/uploads"
AUDIO_OUTPUT_DIR = "app/static/audio"

# Ensure directories exist
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)

# API endpoints
ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1"

# Print debug information
print(f"OPENAI_API_KEY set: {bool(OPENAI_API_KEY)}")
print(f"ELEVENLABS_API_KEY set: {bool(ELEVENLABS_API_KEY)}")