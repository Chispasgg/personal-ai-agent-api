'''
Created on 7 nov 2025

@author: chispas
'''
from beans.services.voice.i_voices.i_tts_provider import TTSProvider


class GTTSProvider(TTSProvider):
    """gTTS-based TTS implementation."""

    def synthesize(self, text: str, language: str="es") -> bytes:
        """Synthesize using gTTS."""
        try:
            from gtts import gTTS
            from io import BytesIO

            tts = gTTS(text=text, lang=language, slow=False)
            audio_fp = BytesIO()
            tts.write_to_fp(audio_fp)
            audio_fp.seek(0)

            print(f"Synthesized speech, length: {len(text)}")
            return audio_fp.read()

        except ImportError:
            print("gTTS not installed")
            return b""
        except Exception as e:
            print(f"TTS synthesis failed, error: {str(e)}")
            return b""
