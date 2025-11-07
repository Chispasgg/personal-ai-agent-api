'''
Created on 6 nov 2025

@author: chispas
'''
from pydantic import BaseModel


class IngestRequest(BaseModel):
    """Request to trigger ingestion."""
    kb_path: str = None
