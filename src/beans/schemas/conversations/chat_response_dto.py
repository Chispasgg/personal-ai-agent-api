'''
Created on 6 nov 2025

@author: chispas
'''
from pydantic import BaseModel, Field
from typing import Optional
from beans.schemas import schemas_litrerals
from beans.schemas.extraction import extracted_data_dto


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""

    reply: str = Field(..., description="Assistant's reply")
    language: str = Field(..., description="Detected/used language")
    sentiment: schemas_litrerals.Sentiment = Field(..., description="Detected user sentiment")
    extracted: extracted_data_dto.ExtractedData = Field(..., description="Extracted structured data")
    missing_fields: list[str] = Field(default_factory=list, description="Still missing fields")
    summary_ready: bool = Field(False, description="Whether summary is ready")
    summary: Optional[str] = Field(None, description="Conversation summary if ready")
    session_id: str = Field(..., description="Session identifier")
    turn_number: int = Field(..., description="Turn number in conversation")
    sound_file_base64: Optional[str] = Field(None, description="Base64-encoded audio file (optional, for STT)")
