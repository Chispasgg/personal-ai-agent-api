"""
Conversation memory management for multi-turn dialogue.
"""
from typing import Dict, List, Optional
from pathlib import Path
from config.settings import settings
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages.base import BaseMessage
from langchain_core.messages.human import HumanMessage
from langchain_core.messages.ai import AIMessage
from utils.jsonio import safe_read_json


class MemoryManager:
    """
    Manages conversation memory per session.
    Uses modern LangChain ChatMessageHistory approach.
    """

    def __init__(self):
        """Initialize memory manager."""
        self._memories: Dict[str, InMemoryChatMessageHistory] = {}
        self._message_counts: Dict[str, int] = {}
        self.storage_path = Path(settings.conversation_storage_path)

    def _load_from_storage(self, session_id: str) -> bool:
        """
        Try to load conversation from storage JSON file.

        Args:
            session_id: Session identifier

        Returns:
            True if session was loaded successfully, False otherwise
        """
        session_file = self.storage_path / f"{session_id}.json"

        if not session_file.exists():
            return False

        try:
            data = safe_read_json(session_file, default=None)
            if data is None:
                return False

            # Create new memory for this session
            memory = InMemoryChatMessageHistory()

            # Load all turns from the stored conversation
            turns = data.get("turns", [])
            for turn in turns:
                user_msg = turn.get("user_message", "")
                assistant_msg = turn.get("assistant_reply", "")

                if user_msg:
                    memory.add_user_message(user_msg)
                if assistant_msg:
                    memory.add_ai_message(assistant_msg)

            # Store in memory cache
            self._memories[session_id] = memory
            self._message_counts[session_id] = len(turns)

            print(f"Loaded session from storage, session_id: {session_id}, turns: {len(turns)}")
            return True

        except Exception as e:
            print(f"Failed to load session from storage, session_id: {session_id}, error: {str(e)}")
            return False

    def get_memory(self, session_id: str) -> InMemoryChatMessageHistory:
        """
        Get or create memory for a session.
        If session doesn't exist in memory, tries to load from storage.

        Args:
            session_id: Unique session identifier

        Returns:
            InMemoryChatMessageHistory instance
        """
        if session_id not in self._memories:
            # Try to load from storage first
            if not self._load_from_storage(session_id):
                # If not found in storage, create new memory
                print(f"Creating new memory for session, session_id: {session_id}")
                self._memories[session_id] = InMemoryChatMessageHistory()
                self._message_counts[session_id] = 0

        return self._memories[session_id]

    def add_message(self, session_id: str, user_message: str, ai_response: str) -> None:
        """
        Add a message exchange to memory.

        Args:
            session_id: Session identifier
            user_message: User's message
            ai_response: AI's response
        """
        memory = self.get_memory(session_id)
        memory.add_user_message(user_message)
        memory.add_ai_message(ai_response)

        self._message_counts[session_id] = self._message_counts.get(session_id, 0) + 1

        # Check if we're approaching the limit
        if self._message_counts[session_id] >= settings.max_conversation_turns:
            print(f"Session approaching max conversation turns, session_id: {session_id}, count: {self._message_counts[session_id]}")

    def get_messages(self, session_id: str) -> List[BaseMessage]:
        """
        Get all messages for a session.

        Args:
            session_id: Session identifier

        Returns:
            List of messages
        """
        if session_id not in self._memories:
            return []

        return self._memories[session_id].messages

    def get_conversation_text(self, session_id: str) -> str:
        """
        Get conversation as formatted text.

        Args:
            session_id: Session identifier

        Returns:
            Formatted conversation string
        """
        messages = self.get_messages(session_id)
        lines = []

        for msg in messages:
            if isinstance(msg, HumanMessage):
                lines.append(f"User: {msg.content}")
            elif isinstance(msg, AIMessage):
                lines.append(f"Assistant: {msg.content}")

        return "\n".join(lines)

    def clear_memory(self, session_id: str) -> None:
        """
        Clear memory for a session.

        Args:
            session_id: Session identifier
        """
        if session_id in self._memories:
            print(f"Clearing memory for session, session_id: {session_id}")
            del self._memories[session_id]
            self._message_counts.pop(session_id, None)

    def get_session_count(self, session_id: str) -> int:
        """
        Get message count for session.

        Args:
            session_id: Session identifier

        Returns:
            Number of message exchanges
        """
        return self._message_counts.get(session_id, 0)

    def has_session(self, session_id: str) -> bool:
        """
        Check if session exists.

        Args:
            session_id: Session identifier

        Returns:
            True if session has memory
        """
        return session_id in self._memories


# Global memory manager instance
_memory_manager: Optional[MemoryManager] = None


def get_memory_manager() -> MemoryManager:
    """
    Get global memory manager instance.

    Returns:
        MemoryManager instance
    """
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager
