'''
Created on 6 nov 2025

@author: chispas
'''
from typing import Optional
from pydantic import BaseModel, Field
from beans.schemas.conversations import conversation_turn_dto
from beans.schemas.extraction import extracted_data_dto


class ConversationSession(BaseModel):
    """Complete conversation session data."""

    session_id: str = Field(..., description="Session identifier")
    start_time: str = Field(..., description="Session start timestamp")
    end_time: Optional[str] = Field(None, description="Session end timestamp")
    language: str = Field(..., description="Primary language")
    turns: list[conversation_turn_dto.ConversationTurn] = Field(default_factory=list, description="Conversation turns")
    final_extracted: Optional[extracted_data_dto.ExtractedData] = Field(None, description="Final extracted data")
    summary: Optional[str] = Field(None, description="Final summary")
    total_turns: int = Field(0, description="Total number of turns")
