'''
Created on 6 nov 2025

@author: chispas
'''
from pydantic import BaseModel, Field
from beans.schemas import schemas_litrerals
from beans.schemas.extraction import extracted_data_dto


class ConversationTurn(BaseModel):
    """Single turn in a conversation."""

    turn_number: int = Field(..., description="Turn sequence number")
    timestamp: str = Field(..., description="ISO timestamp")
    user_message: str = Field(..., description="User's message")
    assistant_reply: str = Field(..., description="Assistant's reply")
    language: str = Field(..., description="Language used")
    sentiment: schemas_litrerals.Sentiment = Field(..., description="Detected sentiment")
    sentiment_polarity_value: float = Field(..., description="Detected sentiment value")
    extracted_delta: extracted_data_dto.ExtractedData = Field(..., description="New data extracted this turn")
