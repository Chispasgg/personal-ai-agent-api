'''
Created on 7 nov 2025

@author: chispas
'''
from abc import ABC, abstractmethod
from pathlib import Path


class STTProvider(ABC):
    """Abstract base for STT providers."""

    @abstractmethod
    def transcribe(self, audio_file: Path) -> str:
        """Transcribe audio to text."""
        pass
