from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Request
from ..models.models import TranscriptionResponse, ChatRequest, ChatResponse, TextToSpeechRequest
from ..services.openai_service import OpenAIService
from ..services.elevenlabs_service import ElevenLabsService
from ..utils.audio_utils import save_upload_file, convert_webm_to_wav
from ..utils.config import DEFAULT_VOICE_ID
from ..utils.db_utils import (
    get_visitor_stats, 
    increment_button_count, 
    check_button_usage, 
    get_total_visitors,
    get_usage_stats
)

router = APIRouter()

# Dependency Injection
def get_openai_service():
    return OpenAIService()

def get_elevenlabs_service():
    return ElevenLabsService()


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    file: UploadFile = File(...), 
    openai_service: OpenAIService = Depends(get_openai_service)
):
    """
    Transcribe an audio file using OpenAI Whisper ASR
    """
    if file.filename is None or not file.filename.endswith(('.webm', '.mp3', '.wav', '.m4a')):
        raise HTTPException(status_code=400, detail="Unsupported file format")
    
    try:
        # Save the uploaded file
        file_path = save_upload_file(file)
        
        # Convert webm to wav if needed
        if file_path.endswith('.webm'):
            file_path = convert_webm_to_wav(file_path)
        
        # Transcribe the audio
        transcription = openai_service.transcribe_audio(file_path)
        
        return {"text": transcription}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error transcribing audio: {str(e)}")


@router.post("/chat", response_model=ChatResponse)
async def chat_completion(
    request: ChatRequest,
    openai_service: OpenAIService = Depends(get_openai_service),
    elevenlabs_service: ElevenLabsService = Depends(get_elevenlabs_service)
):
    """
    Generate a chat response using GPT-4 and convert to speech using ElevenLabs
    """
    try:
        # Get chat completion
        conversation_history = request.conversation_history if request.conversation_history is not None else []
        response_text = openai_service.chat_completion(
            request.message, 
            conversation_history
        )
        
        # Try to convert to speech, but handle the case where ElevenLabs API key is missing
        try:
            audio_url = elevenlabs_service.text_to_speech(response_text)
            
            return {
                "response": response_text,
                "audio_url": audio_url
            }
        except ValueError as e:
            # Return response without audio if there's an API key issue
            print(f"Warning: Could not convert text to speech: {e}")
            return {
                "response": response_text,
                "audio_url": None
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


@router.post("/text-to-speech")
async def text_to_speech(
    request: TextToSpeechRequest,
    elevenlabs_service: ElevenLabsService = Depends(get_elevenlabs_service)
):
    """
    Convert text to speech using ElevenLabs
    """
    try:
        voice_id = request.voice_id if request.voice_id is not None else DEFAULT_VOICE_ID
        try:
            audio_url = elevenlabs_service.text_to_speech(request.text, voice_id)
            return {"audio_url": audio_url}
        except ValueError as e:
            # Specifically catch the API key missing/invalid error
            error_message = str(e)
            if "ELEVENLABS_API_KEY" in error_message or "401 Unauthorized" in error_message:
                raise HTTPException(
                    status_code=401, 
                    detail="ElevenLabs API key is invalid or not set. Please provide a valid API key."
                )
            raise
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error converting text to speech: {str(e)}")


@router.get("/voices")
async def get_voices(elevenlabs_service: ElevenLabsService = Depends(get_elevenlabs_service)):
    """
    Get available voices from ElevenLabs
    """
    try:
        voices = elevenlabs_service.get_available_voices()
        return {"voices": voices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching voices: {str(e)}")


@router.get("/stats")
async def get_stats():
    """
    Get visitor and usage statistics
    """
    try:
        stats = get_usage_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching statistics: {str(e)}")


@router.post("/track-visitor")
async def track_visitor(request: Request):
    """
    Track a visitor by IP address and device info
    """
    try:
        # Get client IP address
        ip_address = request.client.host if request.client else "127.0.0.1"
        # Get device info from user agent
        user_agent = request.headers.get("user-agent", "Unknown")
        
        # Track the visitor
        visitor = get_visitor_stats(ip_address, user_agent)
        
        if visitor:
            return {
                "success": True,
                "visitor_id": visitor['id'],
                "visit_count": visitor['visit_count'],
                "total_visitors": get_total_visitors()
            }
        else:
            return {"success": False, "error": "Failed to track visitor"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tracking visitor: {str(e)}")


@router.post("/check-button-usage/{button_type}")
async def check_usage(button_type: str, request: Request):
    """
    Check if a button's usage limit is reached
    """
    if button_type not in ['record', 'send', 'read']:
        raise HTTPException(status_code=400, detail="Invalid button type")
    
    try:
        # Get client IP address and device info
        ip_address = request.client.host if request.client else "127.0.0.1"
        user_agent = request.headers.get("user-agent", "Unknown")
        
        # Check button usage
        result = check_button_usage(ip_address, user_agent, button_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking button usage: {str(e)}")


@router.post("/increment-button-usage/{button_type}")
async def increment_usage(button_type: str, request: Request):
    """
    Increment the usage count for a specific button
    """
    if button_type not in ['record', 'send', 'read']:
        raise HTTPException(status_code=400, detail="Invalid button type")
    
    try:
        # Get client IP address and device info
        ip_address = request.client.host if request.client else "127.0.0.1"
        user_agent = request.headers.get("user-agent", "Unknown")
        
        # Increment button usage
        visitor = increment_button_count(ip_address, user_agent, button_type)
        
        if visitor:
            # Return the updated counts
            return {
                "success": True,
                f"{button_type}_button_count": visitor[f"{button_type}_button_count"],
                "remaining": max(0, 5 - visitor[f"{button_type}_button_count"])
            }
        else:
            return {"success": False, "error": "Failed to increment button count"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error incrementing button usage: {str(e)}")