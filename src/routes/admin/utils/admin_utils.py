'''
Created on 6 nov 2025

@author: chispas
'''
from config.settings import settings

from fastapi import HTTPException, Header, status


def verify_admin_key(x_api_key: str=Header(None)):
    """Verify admin API key."""
    if x_api_key != settings.api_key_admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
