"""
Unit tests for memory.py module.
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from llm.memory import MemoryManager, get_memory_manager


class TestMemoryManager:
    """Tests for MemoryManager class."""
    
    @pytest.fixture
    def memory_manager(self, tmp_path):
        """Fixture for memory manager with temporary storage."""
        with patch('llm.memory.settings') as mock_settings:
            mock_settings.conversation_storage_path = str(tmp_path / "conversations")
            mock_settings.max_conversation_turns = 50
            manager = MemoryManager()
            return manager
    
    def test_init_creates_empty_memories(self, memory_manager):
        """Test that initialization creates empty memory dict."""
        assert isinstance(memory_manager._memories, dict)
        assert len(memory_manager._memories) == 0
    
    def test_get_memory_creates_new(self, memory_manager):
        """Test get_memory creates new memory for unknown session."""
        session_id = "new-session-123"
        
        memory = memory_manager.get_memory(session_id)
        
        assert memory is not None
        assert session_id in memory_manager._memories
        assert len(memory.messages) == 0
    
    def test_get_memory_returns_existing(self, memory_manager):
        """Test get_memory returns existing memory."""
        session_id = "test-session"
        
        # Get memory twice
        memory1 = memory_manager.get_memory(session_id)
        memory2 = memory_manager.get_memory(session_id)
        
        # Should be same instance
        assert memory1 is memory2
    
    def test_add_message(self, memory_manager):
        """Test adding message to memory."""
        session_id = "test-session"
        
        memory_manager.add_message(
            session_id=session_id,
            user_message="Hola",
            ai_response="¡Hola! ¿En qué puedo ayudarte?"
        )
        
        memory = memory_manager.get_memory(session_id)
        messages = memory.messages
        
        assert len(messages) == 2
        assert messages[0].content == "Hola"
        assert messages[1].content == "¡Hola! ¿En qué puedo ayudarte?"
    
    def test_add_multiple_messages(self, memory_manager):
        """Test adding multiple messages."""
        session_id = "multi-message"
        
        exchanges = [
            ("Hola", "¡Hola!"),
            ("¿Cómo estás?", "Muy bien, gracias"),
            ("Necesito ayuda", "Claro, dime"),
        ]
        
        for user_msg, ai_msg in exchanges:
            memory_manager.add_message(session_id, user_msg, ai_msg)
        
        memory = memory_manager.get_memory(session_id)
        
        # Should have 6 messages (3 pairs)
        assert len(memory.messages) == 6
    
    def test_get_messages(self, memory_manager):
        """Test get_messages returns message list."""
        session_id = "test-session"
        
        memory_manager.add_message(session_id, "User message", "AI response")
        
        messages = memory_manager.get_messages(session_id)
        
        assert len(messages) == 2
        from langchain_core.messages.human import HumanMessage
        from langchain_core.messages.ai import AIMessage
        
        assert isinstance(messages[0], HumanMessage)
        assert isinstance(messages[1], AIMessage)
    
    def test_get_messages_empty_session(self, memory_manager):
        """Test get_messages for nonexistent session returns empty list."""
        messages = memory_manager.get_messages("nonexistent-session")
        
        assert messages == []
    
    def test_get_conversation_text(self, memory_manager):
        """Test get_conversation_text formats messages correctly."""
        session_id = "text-session"
        
        memory_manager.add_message(session_id, "Hola", "¡Hola!")
        memory_manager.add_message(session_id, "¿Cómo estás?", "Bien, gracias")
        
        text = memory_manager.get_conversation_text(session_id)
        
        assert "User: Hola" in text
        assert "Assistant: ¡Hola!" in text
        assert "User: ¿Cómo estás?" in text
        assert "Assistant: Bien, gracias" in text
    
    def test_get_conversation_text_empty(self, memory_manager):
        """Test get_conversation_text for empty session."""
        text = memory_manager.get_conversation_text("empty-session")
        
        assert text == ""
    
    def test_clear_memory(self, memory_manager):
        """Test clearing memory for session."""
        session_id = "clear-test"
        
        # Add messages
        memory_manager.add_message(session_id, "Test", "Response")
        
        # Verify memory exists
        assert session_id in memory_manager._memories
        assert memory_manager.get_session_count(session_id) == 1
        
        # Clear memory
        memory_manager.clear_memory(session_id)
        
        # Verify memory is cleared
        assert session_id not in memory_manager._memories
        assert memory_manager.get_session_count(session_id) == 0
    
    def test_get_session_count(self, memory_manager):
        """Test get_session_count tracks messages correctly."""
        session_id = "count-test"
        
        assert memory_manager.get_session_count(session_id) == 0
        
        memory_manager.add_message(session_id, "Msg 1", "Response 1")
        assert memory_manager.get_session_count(session_id) == 1
        
        memory_manager.add_message(session_id, "Msg 2", "Response 2")
        assert memory_manager.get_session_count(session_id) == 2
    
    def test_has_session(self, memory_manager):
        """Test has_session checks for session existence."""
        session_id = "exists-test"
        
        assert memory_manager.has_session(session_id) is False
        
        memory_manager.get_memory(session_id)
        
        assert memory_manager.has_session(session_id) is True
    
    def test_max_conversation_turns_warning(self, memory_manager, capsys):
        """Test warning when approaching max turns."""
        session_id = "max-turns-test"
        
        # Mock settings to have a low limit
        with patch('llm.memory.settings') as mock_settings:
            mock_settings.max_conversation_turns = 2
            
            # Add messages to reach the limit
            memory_manager.add_message(session_id, "Test 1", "Response 1")
            memory_manager.add_message(session_id, "Test 2", "Response 2")
            
            captured = capsys.readouterr()
            assert "approaching max conversation turns" in captured.out
    
    def test_load_from_storage_nonexistent(self, memory_manager):
        """Test _load_from_storage with nonexistent file."""
        result = memory_manager._load_from_storage("nonexistent-session")
        
        assert result is False
    
    def test_load_from_storage_with_existing_file(self, memory_manager, tmp_path):
        """Test _load_from_storage loads existing session."""
        session_id = "stored-session"
        
        # Create a stored session file
        storage_path = Path(memory_manager.storage_path)
        storage_path.mkdir(parents=True, exist_ok=True)
        
        session_data = {
            "session_id": session_id,
            "turns": [
                {
                    "user_message": "Hola",
                    "assistant_reply": "¡Hola!"
                },
                {
                    "user_message": "¿Cómo estás?",
                    "assistant_reply": "Bien, gracias"
                }
            ]
        }
        
        session_file = storage_path / f"{session_id}.json"
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
        
        # Load from storage
        result = memory_manager._load_from_storage(session_id)
        
        assert result is True
        assert session_id in memory_manager._memories
        
        messages = memory_manager.get_messages(session_id)
        assert len(messages) == 4  # 2 turns = 4 messages
    
    def test_load_from_storage_corrupted_file(self, memory_manager, tmp_path):
        """Test _load_from_storage with corrupted file."""
        session_id = "corrupted-session"
        
        # Create corrupted file
        storage_path = Path(memory_manager.storage_path)
        storage_path.mkdir(parents=True, exist_ok=True)
        
        session_file = storage_path / f"{session_id}.json"
        with open(session_file, 'w') as f:
            f.write("{ invalid json }")
        
        result = memory_manager._load_from_storage(session_id)
        
        assert result is False
    
    def test_get_memory_loads_from_storage(self, memory_manager, tmp_path):
        """Test that get_memory tries to load from storage."""
        session_id = "auto-load-session"
        
        # Create stored session
        storage_path = Path(memory_manager.storage_path)
        storage_path.mkdir(parents=True, exist_ok=True)
        
        session_data = {
            "session_id": session_id,
            "turns": [
                {"user_message": "Test", "assistant_reply": "Response"}
            ]
        }
        
        with open(storage_path / f"{session_id}.json", 'w') as f:
            json.dump(session_data, f)
        
        # Get memory (should load from storage)
        memory = memory_manager.get_memory(session_id)
        
        messages = memory.messages
        assert len(messages) == 2


class TestMemoryManagerSingleton:
    """Tests for memory manager singleton pattern."""
    
    def test_get_memory_manager_returns_instance(self):
        """Test that get_memory_manager returns MemoryManager instance."""
        manager = get_memory_manager()
        
        assert isinstance(manager, MemoryManager)
    
    def test_get_memory_manager_singleton(self):
        """Test that get_memory_manager returns same instance."""
        # Reset global manager
        import llm.memory
        llm.memory._memory_manager = None
        
        manager1 = get_memory_manager()
        manager2 = get_memory_manager()
        
        assert manager1 is manager2
