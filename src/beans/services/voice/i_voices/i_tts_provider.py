'''
Created on 7 nov 2025

@author: chispas
'''
from abc import ABC, abstractmethod


class TTSProvider(ABC):
    """Abstract base for TTS providers."""

    @abstractmethod
    def synthesize(self, text: str, language: str="es") -> bytes:
        """Synthesize text to audio."""
        pass
