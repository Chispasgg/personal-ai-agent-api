'''
Created on 6 nov 2025

@author: chispas
'''
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field("ok", description="Service status")
    version: str = Field(..., description="API version")
