'''
Created on 6 nov 2025

@author: chispas
'''
from typing import  Literal

# Literal type for converastions DTOs
Sentiment = Literal["negative", "neutral", "positive"]
Category = Literal["shipping", "billing", "technical", "other"]
Urgency = Literal["low", "medium", "high"]
