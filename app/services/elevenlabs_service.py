import requests
import os
import sys
from ..utils.config import ELEVENLABS_API_KEY, ELEVENLABS_API_URL, DEFAULT_VOICE_ID
from ..utils.audio_utils import save_audio_response

class ElevenLabsService:
    def __init__(self):
        """Initialize the ElevenLabs service"""
        self.api_key = ELEVENLABS_API_KEY
        
        # Check if API key is available
        if not self.api_key:
            print("ERROR: ELEVENLABS_API_KEY is not set or empty!", file=sys.stderr)
            print("Text-to-speech functionality will not work without a valid API key.", file=sys.stderr)
            
        self.api_url = ELEVENLABS_API_URL
        self.headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key or ""  # Prevent None being passed as a header value
        }
    
    def text_to_speech(self, text: str, voice_id: str = DEFAULT_VOICE_ID) -> str:
        """
        Convert text to speech using ElevenLabs API
        Returns the URL path to the generated audio file
        """
        # Early check for API key
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY environment variable is not set. Please set it to use text-to-speech features.")
            
        url = f"{self.api_url}/text-to-speech/{voice_id}/stream"
        
        # Detect if text contains Chinese characters to use multilingual model
        def contains_chinese(text):
            return any('\u4e00' <= char <= '\u9fff' for char in text)
        
        has_chinese = contains_chinese(text)
        
        # Safety check - if using non-standard voice ID with Chinese text, fall back to a safe voice
        if has_chinese and voice_id != DEFAULT_VOICE_ID:
            try:
                # For non-default voices, check if that voice exists first
                check_voice_url = f"{self.api_url}/voices/{voice_id}"
                check_response = requests.get(check_voice_url, headers={"xi-api-key": self.api_key})
                
                if check_response.status_code != 200:
                    print(f"Voice ID {voice_id} not found or not accessible. Falling back to default voice.", file=sys.stderr)
                    voice_id = DEFAULT_VOICE_ID  # Fall back to Rachel which always works
            except Exception as e:
                print(f"Error checking voice availability: {e}", file=sys.stderr)
                voice_id = DEFAULT_VOICE_ID  # Fallback on any error
        
        # Use multilingual model for Chinese text to improve pronunciation
        model_id = "eleven_multilingual_v2" if has_chinese else "eleven_monolingual_v1"
        
        data = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        print(f"Text to speech request: Voice ID={voice_id}, Model={model_id}, Contains Chinese={has_chinese}", file=sys.stderr)
        
        try:
            print(f"Sending request to ElevenLabs API at {url}")
            print(f"Using API key starting with: {self.api_key[:4]}..." if self.api_key else "No API key available")
            
            response = requests.post(url, json=data, headers=self.headers)
            
            # Debug response
            if response.status_code != 200:
                print(f"ElevenLabs API response status: {response.status_code}", file=sys.stderr)
                try:
                    error_details = response.json()
                    print(f"Error details: {error_details}", file=sys.stderr)
                except:
                    print(f"Error content: {response.text[:200]}", file=sys.stderr)
            
            # Check for specific status codes
            if response.status_code == 401:
                raise ValueError("ElevenLabs API returned 401 Unauthorized. Your API key may be invalid or expired.")
            elif response.status_code == 403:
                raise ValueError(f"ElevenLabs API returned 403 Forbidden. You may not have permission to use voice {voice_id} or requested model {model_id}.")
            elif response.status_code == 404:
                # Specifically handle voice not found
                raise ValueError(f"Voice ID {voice_id} not found. Please try a different voice.")
            elif response.status_code == 422:
                raise ValueError(f"Invalid request to ElevenLabs API: The request data may be incorrect or the voice {voice_id} may not support this model {model_id}.")
                
            response.raise_for_status()
            
            # Save the audio file and return its URL
            return save_audio_response(response.content)
        except requests.RequestException as e:
            error_msg = f"Error connecting to ElevenLabs API: {e}"
            print(error_msg, file=sys.stderr)
            # If this is a premium voice that's not available, try with default voice
            if voice_id != DEFAULT_VOICE_ID:
                print(f"Retrying with default voice {DEFAULT_VOICE_ID}", file=sys.stderr)
                return self.text_to_speech(text, DEFAULT_VOICE_ID)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Error converting text to speech: {e}"
            print(error_msg, file=sys.stderr)
            raise ValueError(error_msg)  # Convert all errors to ValueError for consistent handling
    
    def get_available_voices(self):
        """
        Get a list of available voices from ElevenLabs
        """
        # Early check for API key
        if not self.api_key:
            # Return default voice only if no API key
            return [{"voice_id": DEFAULT_VOICE_ID, "name": "Rachel (Default)"}]
            
        url = f"{self.api_url}/voices"
        
        try:
            response = requests.get(
                url, 
                headers={"xi-api-key": self.api_key}
            )
            
            # Check for specific status codes
            if response.status_code == 401:
                print("ElevenLabs API returned 401 Unauthorized for voices request. Using default voice only.", file=sys.stderr)
                return [{"voice_id": DEFAULT_VOICE_ID, "name": "Rachel (Default)"}]
                
            response.raise_for_status()
            
            return response.json()["voices"]
        except Exception as e:
            print(f"Error fetching voices: {e}", file=sys.stderr)
            # Return default voice on error
            return [{"voice_id": DEFAULT_VOICE_ID, "name": "Rachel (Default)"}]