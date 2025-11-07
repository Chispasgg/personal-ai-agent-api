"""
Speech-to-Text and Text-to-Speech service with pluggable implementations.
"""

from typing import Optional
from pathlib import Path
from config.settings import settings
from beans.services.voice.im_voices.im_no_op_stt import NoOpSTT
from beans.services.voice.im_voices.im_gtts_provider import GTTSProvider


class STTTTSService:
    """Combined STT/TTS service."""

    def __init__(self):
        """Initialize service with configured providers."""
        # Initialize STT provider, audio to text
        self.stt_enabled = settings.stt_enabled
        # Initialize STT provider, texto to audio
        self.tts_enabled = settings.tts_enabled

        # Initialize providers
        self.stt = NoOpSTT()  # Default stub

        if self.tts_enabled and settings.tts_provider == "gtts":
            self.tts = GTTSProvider()
        else:
            self.tts = None

    def transcribe_audio(self, audio_file: Path) -> Optional[str]:
        """Transcribe audio if STT is enabled."""
        if not self.stt_enabled:
            return None

        return self.stt.transcribe(audio_file)

    def text_to_speech(self, text: str, language: str="es") -> Optional[bytes]:
        """Convert text to speech if TTS is enabled."""
        if not self.tts_enabled or self.tts is None:
            return None

        return self.tts.synthesize(text, language)


# Global service
_stt_tts_service = None


def get_stt_tts_service() -> STTTTSService:
    """Get global STT/TTS service."""
    global _stt_tts_service
    if _stt_tts_service is None:
        _stt_tts_service = STTTTSService()
    return _stt_tts_service
