'''
Created on 6 nov 2025

@author: chispas
'''
from typing import Optional, List
from pydantic import BaseModel, Field
from beans.schemas.summary import summary_key_point_dto


class ConversationSummary(BaseModel):
    """Comprehensive conversation summary."""

    session_id: str = Field(..., description="Session identifier")
    summary_text: str = Field(..., description="Main summary text")
    key_points: List[summary_key_point_dto.SummaryKeyPoint] = Field(default_factory=list, description="Key points")
    problem_category: Optional[str] = Field(None, description="Identified problem category")
    urgency_level: Optional[str] = Field(None, description="Urgency level")
    customer_sentiment: str = Field("neutral", description="Overall customer sentiment")
    resolution_status: str = Field("pending", description="Resolution status")
    next_steps: List[str] = Field(default_factory=list, description="Suggested next steps")
    total_turns: int = Field(0, description="Number of conversation turns")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session-123",
                "summary_text": "Customer reported shipping delay for order ABC123456",
                "key_points": [
                    {"point": "Order not received after 2 weeks", "category": "shipping"},
                    {"point": "Customer requests urgent resolution", "category": "urgency"}
                ],
                "problem_category": "shipping",
                "urgency_level": "high",
                "customer_sentiment": "negative",
                "resolution_status": "pending",
                "next_steps": [
                    "Track package location",
                    "Contact shipping provider",
                    "Update customer within 24h"
                ],
                "total_turns": 5
            }
        }
