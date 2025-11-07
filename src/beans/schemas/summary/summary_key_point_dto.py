'''
Created on 6 nov 2025

@author: chispas
'''

from typing import Optional
from pydantic import BaseModel, Field


class SummaryKeyPoint(BaseModel):
    """A key point in the conversation summary."""

    point: str = Field(..., description="Key point description")
    category: Optional[str] = Field(None, description="Point category")
