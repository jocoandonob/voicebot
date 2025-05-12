from typing import List, Dict, Optional
from pydantic import BaseModel

class TranscriptionResponse(BaseModel):
    text: str

class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[Dict]] = []

class ChatResponse(BaseModel):
    response: str
    audio_url: Optional[str] = None

class TextToSpeechRequest(BaseModel):
    text: str
    voice_id: Optional[str] = "21m00Tcm4TlvDq8ikWAM"  # Default voice ID (Rachel)

class UsageStats(BaseModel):
    total_visitors: int
    total_visits: int
    total_record_uses: int
    total_send_uses: int
    total_read_uses: int

class VisitorResponse(BaseModel):
    success: bool
    visitor_id: Optional[int] = None
    visit_count: Optional[int] = None
    total_visitors: Optional[int] = None
    error: Optional[str] = None

class ButtonUsageCheck(BaseModel):
    allowed: bool
    remaining: int

class ButtonUsageIncrement(BaseModel):
    success: bool
    record_button_count: Optional[int] = None
    send_button_count: Optional[int] = None
    read_button_count: Optional[int] = None
    remaining: Optional[int] = None
    error: Optional[str] = None