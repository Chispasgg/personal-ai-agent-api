'''
Created on 6 nov 2025

@author: chispas
'''
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from config.settings import settings


class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""

    session_id: str = Field(..., description="Unique session identifier")
    message: str = Field(..., description="User message", min_length=1)
    language: Optional[str] = Field(None, description="Optional language hint")
    audio_response: bool = Field(False, description="If sound response is needed")

    @field_validator("message")
    @classmethod
    def validate_message_length(cls, v: str) -> str:
        """Validate message length."""
        if len(v) > settings.max_message_length:
            raise ValueError(f"Message exceeds maximum length of {settings.max_message_length}")

        return v.strip()

    @field_validator("session_id")
    @classmethod
    def validate_session_id(cls, v: str) -> str:
        """Validate session ID format."""
        if not v or len(v) < 3:
            raise ValueError("Session ID must be at least 3 characters")

        return v.strip()
