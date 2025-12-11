from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class Fact(BaseModel):
    type: str
    value: str
    confidence: float = Field(ge=0.0, le=1.0)
    source: str


class Preference(BaseModel):
    category: str
    value: str
    confidence: float = Field(ge=0.0, le=1.0)
    source: str


class MirrorFacts(BaseModel):
    subject_id: str
    facts: List[Fact]
    preferences: List[Preference]


class StyleGuide(BaseModel):
    subject_id: str
    tone: str
    writing_examples: List[str]
    response_tips: List[str]


class ChatRequest(BaseModel):
    subject_id: str
    message: str
    voice: Optional[bool] = False
    voice_id: Optional[str] = None


class RetrievedItem(BaseModel):
    text: str
    metadata: Dict[str, Any]
    score: float


class ChatResponse(BaseModel):
    reply: str
    citations: List[Dict[str, Any]]
    audio_url: Optional[str] = None
