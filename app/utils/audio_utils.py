import os
import uuid
import subprocess
from fastapi import UploadFile
import soundfile as sf
from pydub import AudioSegment

from .config import UPLOADS_DIR, AUDIO_OUTPUT_DIR

def save_upload_file(file: UploadFile):
    """Save an uploaded file and return the file path"""
    # Create a unique filename
    filename = f"{uuid.uuid4()}{os.path.splitext(file.filename or 'audio')[1]}"
    filepath = os.path.join(UPLOADS_DIR, filename)
    
    # Save the file
    with open(filepath, "wb") as f:
        f.write(file.file.read())
    
    return filepath

def convert_webm_to_wav(webm_path):
    """Convert a webm file to wav format"""
    # Create output wav filename
    wav_filename = f"{os.path.splitext(os.path.basename(webm_path))[0]}.wav"
    wav_path = os.path.join(UPLOADS_DIR, wav_filename)
    
    try:
        # Convert using pydub
        audio = AudioSegment.from_file(webm_path)
        audio.export(wav_path, format="wav")
        
        # Remove the original webm file
        os.remove(webm_path)
        
        return wav_path
    except Exception as e:
        # Fallback to ffmpeg if pydub fails
        try:
            subprocess.run(
                ["ffmpeg", "-i", webm_path, "-ar", "16000", wav_path],
                check=True
            )
            
            # Remove the original webm file
            os.remove(webm_path)
            
            return wav_path
        except Exception as e:
            print(f"Error converting webm to wav: {e}")
            # Return original if conversion fails
            return webm_path

def save_audio_response(audio_data):
    """Save audio response from ElevenLabs and return the URL path"""
    # Create a unique filename
    filename = f"{uuid.uuid4()}.mp3"
    filepath = os.path.join(AUDIO_OUTPUT_DIR, filename)
    
    # Save the audio data
    with open(filepath, "wb") as f:
        f.write(audio_data)
    
    # Return the URL path
    return f"/static/audio/{filename}"