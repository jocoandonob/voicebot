import os
import sys
from typing import List, Dict, Optional
from openai import OpenAI
from ..utils.config import OPENAI_API_KEY

class OpenAIService:
    def __init__(self):
        """Initialize the OpenAI service"""
        self.api_key = OPENAI_API_KEY
        
        # Check if API key is available
        if not self.api_key:
            print("ERROR: OPENAI_API_KEY is not set or empty!", file=sys.stderr)
            print("Speech recognition and chat functionality will not work without a valid API key.", file=sys.stderr)
            
        self.client = OpenAI(api_key=self.api_key)
    
    def transcribe_audio(self, audio_file_path: str) -> str:
        """
        Transcribe audio using OpenAI's Whisper ASR
        """
        # Early check for API key
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it to use speech recognition features.")
            
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            return transcript.text
        except Exception as e:
            print(f"Error transcribing audio: {e}", file=sys.stderr)
            raise
    
    def chat_completion(self, message: str, conversation_history: Optional[List[Dict]] = None) -> str:
        """
        Generate a response using OpenAI's GPT-4 model
        """
        # Early check for API key
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set. Please set it to use chat functionality.")
            
        # Ensure conversation_history is never None
        history = conversation_history if conversation_history is not None else []

        # Create system message
        system_message = {
            "role": "system", 
            "content": "You are a helpful voice assistant. Provide concise and useful responses."
        }
        
        # Format conversation history - ensure proper types for OpenAI API
        formatted_messages = [
            {"role": "system", "content": system_message["content"]}
        ]
        
        # Add conversation history
        for msg in history:
            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                formatted_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Add the new user message
        formatted_messages.append({"role": "user", "content": message})
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",  # Using the latest GPT-4 model
                messages=formatted_messages,
                max_tokens=300,
                temperature=0.7,
            )
            content = response.choices[0].message.content
            if content is None:
                return "I'm sorry, I couldn't generate a response. Please try again."
            return content
        except Exception as e:
            print(f"Error generating chat response: {e}", file=sys.stderr)
            raise