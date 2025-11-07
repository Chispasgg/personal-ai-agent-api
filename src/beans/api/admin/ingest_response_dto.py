'''
Created on 6 nov 2025

@author: chispas
'''
from pydantic import BaseModel


class IngestResponse(BaseModel):
    """Ingestion response."""
    status: str
    message: str
