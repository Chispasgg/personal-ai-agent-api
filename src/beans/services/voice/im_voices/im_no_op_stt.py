'''
Created on 7 nov 2025

@author: chispas
'''
from beans.services.voice.i_voices.i_stt_provider import STTProvider
from pathlib import Path


class NoOpSTT(STTProvider):
    """No-op STT implementation (stub)."""

    def transcribe(self, audio_file: Path) -> str:
        """Return placeholder text."""
        print("STT not implemented, returning placeholder")
        return "[Audio transcription not available]"
