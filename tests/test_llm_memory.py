"""
Tests for LLM memory management.
"""
import pytest
from unittest.mock import Mock, patch
from src.llm.memory import MemoryManager, get_memory_manager


@pytest.fixture
def memory_manager():
    """Create memory manager instance."""
    return MemoryManager()


class TestMemoryManager:
    """Tests for MemoryManager."""
    
    def test_initialization(self, memory_manager):
        """Test memory manager initialization."""
        assert memory_manager is not None
        assert hasattr(memory_manager, '_memories')
        assert len(memory_manager._memories) == 0
    
    def test_get_memory_new_session(self, memory_manager):
        """Test getting memory for new session."""
        session_id = "new-session-123"
        memory = memory_manager.get_memory(session_id)
        
        assert memory is not None
        assert session_id in memory_manager._memories
    
    def test_get_memory_existing_session(self, memory_manager):
        """Test getting memory for existing session."""
        session_id = "existing-session"
        
        # Create memory first time
        memory1 = memory_manager.get_memory(session_id)
        
        # Get same memory second time
        memory2 = memory_manager.get_memory(session_id)
        
        assert memory1 is memory2
    
    def test_add_message(self, memory_manager):
        """Test adding messages to memory."""
        session_id = "test-session"
        
        memory_manager.add_message(
            session_id,
            user_message="Hello",
            ai_response="Hi there"
        )
        
        messages = memory_manager.get_messages(session_id)
        assert len(messages) == 2
        assert messages[0].content == "Hello"
        assert messages[1].content == "Hi there"
    
    def test_add_multiple_messages(self, memory_manager):
        """Test adding multiple messages."""
        session_id = "multi-message-session"
        
        for i in range(5):
            memory_manager.add_message(
                session_id,
                user_message=f"User message {i}",
                ai_response=f"Assistant response {i}"
            )
        
        messages = memory_manager.get_messages(session_id)
        assert len(messages) == 10  # 5 pairs of messages
    
    def test_get_conversation_text(self, memory_manager):
        """Test getting conversation as text."""
        session_id = "text-session"
        
        memory_manager.add_message(
            session_id,
            user_message="What's my order status?",
            ai_response="Let me check that for you."
        )
        
        text = memory_manager.get_conversation_text(session_id)
        
        assert "What's my order status?" in text
        assert "Let me check that for you." in text
    
    def test_get_session_count(self, memory_manager):
        """Test getting session turn count."""
        session_id = "count-session"
        
        # Initially should be 0
        assert memory_manager.get_session_count(session_id) == 0
        
        # Add messages
        memory_manager.add_message(session_id, "msg1", "resp1")
        assert memory_manager.get_session_count(session_id) == 1
        
        memory_manager.add_message(session_id, "msg2", "resp2")
        assert memory_manager.get_session_count(session_id) == 2
    
    def test_clear_memory(self, memory_manager):
        """Test clearing session memory."""
        session_id = "clear-session"
        
        # Add messages
        memory_manager.add_message(session_id, "Test", "Response")
        assert memory_manager.get_session_count(session_id) == 1
        
        # Clear memory
        memory_manager.clear_memory(session_id)
        
        # Should be empty
        assert memory_manager.get_session_count(session_id) == 0
        assert len(memory_manager.get_messages(session_id)) == 0
    
    def test_clear_nonexistent_session(self, memory_manager):
        """Test clearing memory for non-existent session."""
        # Should not raise error
        memory_manager.clear_memory("nonexistent-session")
    
    def test_get_messages_empty_session(self, memory_manager):
        """Test getting messages from empty session."""
        messages = memory_manager.get_messages("empty-session")
        assert messages == []
    
    def test_memory_isolation(self, memory_manager):
        """Test that sessions are isolated."""
        session1 = "session-1"
        session2 = "session-2"
        
        memory_manager.add_message(session1, "Message 1", "Response 1")
        memory_manager.add_message(session2, "Message 2", "Response 2")
        
        messages1 = memory_manager.get_messages(session1)
        messages2 = memory_manager.get_messages(session2)
        
        assert len(messages1) == 2
        assert len(messages2) == 2
        assert messages1[0].content != messages2[0].content


class TestGetMemoryManager:
    """Tests for get_memory_manager singleton."""
    
    def test_singleton_pattern(self):
        """Test that get_memory_manager returns same instance."""
        manager1 = get_memory_manager()
        manager2 = get_memory_manager()
        
        assert manager1 is manager2
    
    def test_shared_state(self):
        """Test that state is shared across singleton calls."""
        manager1 = get_memory_manager()
        
        # Clear any existing data for this session
        session_id = "test-shared-state-123"
        manager1.clear_memory(session_id)
        
        manager1.add_message(session_id, "Hello", "Hi")
        
        manager2 = get_memory_manager()
        messages = manager2.get_messages(session_id)
        
        assert len(messages) == 2


class TestMemoryLimits:
    """Tests for memory limits and performance."""
    
    def test_large_conversation(self, memory_manager):
        """Test handling large conversations."""
        session_id = "large-session"
        
        # Add many messages
        for i in range(100):
            memory_manager.add_message(
                session_id,
                user_message=f"Message {i}",
                ai_response=f"Response {i}"
            )
        
        messages = memory_manager.get_messages(session_id)
        assert len(messages) == 200  # 100 pairs
        
        # Verify count
        assert memory_manager.get_session_count(session_id) == 100
    
    def test_long_messages(self, memory_manager):
        """Test handling very long messages."""
        session_id = "long-message-session"
        long_text = "A" * 10000  # 10k characters
        
        memory_manager.add_message(
            session_id,
            user_message=long_text,
            ai_response=long_text
        )
        
        text = memory_manager.get_conversation_text(session_id)
        assert len(text) >= 20000


class TestMemoryPersistence:
    """Tests for memory persistence behavior."""
    
    def test_memory_survives_multiple_calls(self, memory_manager):
        """Test that memory persists across multiple operations."""
        session_id = "persist-session"
        
        # Add initial message
        memory_manager.add_message(session_id, "First", "First response")
        
        # Get conversation text
        text1 = memory_manager.get_conversation_text(session_id)
        
        # Add another message
        memory_manager.add_message(session_id, "Second", "Second response")
        
        # Get conversation text again
        text2 = memory_manager.get_conversation_text(session_id)
        
        # Second text should contain both conversations
        assert "First" in text2
        assert "Second" in text2
        assert len(text2) > len(text1)
