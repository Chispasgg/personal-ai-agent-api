"""
Conversation storage service using JSON files.
"""
from pathlib import Path
from datetime import datetime
from typing import Optional
from config.settings import settings
from utils.jsonio import write_json, safe_read_json
from beans.schemas.conversations.conversation_session_dto import ConversationSession
from beans.schemas.extraction.extracted_data_dto import ExtractedData
from beans.schemas.conversations.conversation_turn_dto import ConversationTurn


class StorageService:
    """Manages conversation persistence to JSON files."""

    def __init__(self):
        """Initialize storage service."""
        self.storage_path = Path(settings.conversation_storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def _get_session_file(self, session_id: str) -> Path:
        """Get file path for session."""
        return self.storage_path / f"{session_id}.json"

    def load_session(self, session_id: str) -> Optional[ConversationSession]:
        """
        Load conversation session from disk.

        Args:
            session_id: Session identifier

        Returns:
            ConversationSession or None if not found
        """
        file_path = self._get_session_file(session_id)

        try:
            data = safe_read_json(file_path, default=None)
            if data is None:
                return None

            return ConversationSession(**data)
        except Exception as e:
            print(f"Failed to load session, session_id: {session_id}, error: {str(e)}")
            return None

    def save_session(self, session: ConversationSession) -> None:
        """
        Save conversation session to disk.

        Args:
            session: ConversationSession to save
        """
        file_path = self._get_session_file(session.session_id)

        try:
            write_json(file_path, session.model_dump())
            print(f"Saved session, session_id: {session.session_id}, turns: {len(session.turns)}")
        except Exception as e:
            print(f"Failed to save session, session_id: {session.session_id}, error: {str(e)}")
            raise

    def add_turn(
        self,
        session_id: str,
        turn_number: int,
        user_message: str,
        assistant_reply: str,
        language: str,
        sentiment: str,
        sentiment_polarity_value:float,
        extracted_delta: ExtractedData
    ) -> None:
        """
        Add a conversation turn to session.

        Args:
            session_id: Session identifier
            turn_number: Turn sequence number
            user_message: User's message
            assistant_reply: Assistant's reply
            language: Language used
            sentiment: Detected sentiment
            extracted_delta: New extracted data
        """
        session = self.load_session(session_id)

        if session is None:
            # Create new session
            session = ConversationSession(
                session_id=session_id,
                start_time=datetime.utcnow().isoformat(),
                language=language,
                turns=[],
                total_turns=0
            )

        # Create turn
        turn = ConversationTurn(
            turn_number=turn_number,
            timestamp=datetime.utcnow().isoformat(),
            user_message=user_message,
            assistant_reply=assistant_reply,
            language=language,
            sentiment=sentiment,
            sentiment_polarity_value=sentiment_polarity_value,
            extracted_delta=extracted_delta
        )

        session.turns.append(turn)
        session.total_turns = len(session.turns)

        # Save updated session
        self.save_session(session)

    def finalize_session(
        self,
        session_id: str,
        final_extracted: ExtractedData,
        summary: str
    ) -> None:
        """
        Finalize session with final extracted data and summary.

        Args:
            session_id: Session identifier
            final_extracted: Final complete extracted data
            summary: Conversation summary
        """
        session = self.load_session(session_id)

        if session is None:
            print(f"Cannot finalize non-existent session, session_id: {session_id}")
            return

        session.end_time = datetime.utcnow().isoformat()
        session.final_extracted = final_extracted
        session.summary = summary

        self.save_session(session)
        print(f"Finalized session, session_id: {session_id}")


# Global storage service
_storage_service: Optional[StorageService] = None


def get_storage_service() -> StorageService:
    """Get global storage service instance."""
    global _storage_service
    if _storage_service is None:
        _storage_service = StorageService()
    return _storage_service
