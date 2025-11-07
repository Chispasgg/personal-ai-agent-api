"""
Unit tests for storage.py service.
"""
import pytest
import sys
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, Mock

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from services.storage import StorageService, get_storage_service
from beans.schemas.conversations.conversation_session_dto import ConversationSession
from beans.schemas.extraction.extracted_data_dto import ExtractedData


class TestStorageService:
    """Tests for StorageService class."""
    
    @pytest.fixture
    def storage_service(self, tmp_path):
        """Fixture for storage service with temporary directory."""
        with patch('services.storage.settings') as mock_settings:
            mock_settings.conversation_storage_path = str(tmp_path / "conversations")
            service = StorageService()
            return service
    
    def test_init_creates_storage_directory(self, tmp_path):
        """Test that initialization creates storage directory."""
        storage_path = tmp_path / "test_storage"
        
        with patch('services.storage.settings') as mock_settings:
            mock_settings.conversation_storage_path = str(storage_path)
            service = StorageService()
        
        assert storage_path.exists()
        assert storage_path.is_dir()
    
    def test_get_session_file(self, storage_service):
        """Test _get_session_file generates correct path."""
        session_id = "test-123"
        expected_file = storage_service.storage_path / f"{session_id}.json"
        
        result = storage_service._get_session_file(session_id)
        
        assert result == expected_file
    
    def test_load_session_nonexistent(self, storage_service):
        """Test loading nonexistent session returns None."""
        result = storage_service.load_session("nonexistent-session")
        
        assert result is None
    
    def test_save_and_load_session(self, storage_service, sample_conversation_session):
        """Test saving and loading a session."""
        # Save session
        storage_service.save_session(sample_conversation_session)
        
        # Load session
        loaded = storage_service.load_session(sample_conversation_session.session_id)
        
        assert loaded is not None
        assert loaded.session_id == sample_conversation_session.session_id
        assert loaded.language == sample_conversation_session.language
        assert len(loaded.turns) == len(sample_conversation_session.turns)
    
    def test_save_session_creates_file(self, storage_service, sample_conversation_session):
        """Test that save_session creates JSON file."""
        storage_service.save_session(sample_conversation_session)
        
        session_file = storage_service._get_session_file(sample_conversation_session.session_id)
        
        assert session_file.exists()
        
        # Verify JSON content
        with open(session_file, 'r') as f:
            data = json.load(f)
        
        assert data['session_id'] == sample_conversation_session.session_id
        assert 'turns' in data
    
    def test_add_turn_new_session(self, storage_service):
        """Test adding turn to new session."""
        session_id = "new-session-123"
        
        storage_service.add_turn(
            session_id=session_id,
            turn_number=1,
            user_message="Hola",
            assistant_reply="¡Hola! ¿En qué puedo ayudarte?",
            language="es",
            sentiment="neutral",
            sentiment_polarity_value=0.0,
            extracted_delta=ExtractedData()
        )
        
        # Load and verify
        session = storage_service.load_session(session_id)
        
        assert session is not None
        assert session.session_id == session_id
        assert len(session.turns) == 1
        assert session.turns[0].user_message == "Hola"
        assert session.turns[0].assistant_reply == "¡Hola! ¿En qué puedo ayudarte?"
    
    def test_add_turn_existing_session(self, storage_service, sample_conversation_session):
        """Test adding turn to existing session."""
        # Save initial session with 1 turn
        storage_service.save_session(sample_conversation_session)
        
        # Add another turn
        storage_service.add_turn(
            session_id=sample_conversation_session.session_id,
            turn_number=2,
            user_message="Mi pedido ABC123456",
            assistant_reply="Entiendo, ¿cuál es el problema?",
            language="es",
            sentiment="neutral",
            sentiment_polarity_value=0.0,
            extracted_delta=ExtractedData(order_id="ABC123456")
        )
        
        # Load and verify
        session = storage_service.load_session(sample_conversation_session.session_id)
        
        assert len(session.turns) == 2
        assert session.total_turns == 2
        assert session.turns[1].user_message == "Mi pedido ABC123456"
        assert session.turns[1].extracted_delta.order_id == "ABC123456"
    
    def test_add_multiple_turns(self, storage_service):
        """Test adding multiple turns sequentially."""
        session_id = "multi-turn-session"
        
        messages = [
            ("Hola", "¡Hola!"),
            ("Necesito ayuda", "Claro, ¿qué necesitas?"),
            ("Mi pedido ABC123", "Entiendo el problema"),
        ]
        
        for i, (user_msg, assistant_msg) in enumerate(messages, 1):
            storage_service.add_turn(
                session_id=session_id,
                turn_number=i,
                user_message=user_msg,
                assistant_reply=assistant_msg,
                language="es",
                sentiment="neutral",
                sentiment_polarity_value=0.0,
                extracted_delta=ExtractedData()
            )
        
        session = storage_service.load_session(session_id)
        
        assert len(session.turns) == 3
        assert session.total_turns == 3
    
    def test_finalize_session(self, storage_service, sample_conversation_session):
        """Test finalizing a session with summary and extracted data."""
        # Save initial session
        storage_service.save_session(sample_conversation_session)
        
        # Prepare final data
        final_extracted = ExtractedData(
            order_id="ABC123456",
            category="shipping",
            description="Pedido no llegó",
            urgency="high"
        )
        summary = "Cliente reporta problema con pedido ABC123456. Urgencia alta."
        
        # Finalize
        storage_service.finalize_session(
            session_id=sample_conversation_session.session_id,
            final_extracted=final_extracted,
            summary=summary
        )
        
        # Load and verify
        session = storage_service.load_session(sample_conversation_session.session_id)
        
        assert session.end_time is not None
        assert session.final_extracted is not None
        assert session.final_extracted.order_id == "ABC123456"
        assert session.summary == summary
    
    def test_finalize_nonexistent_session(self, storage_service, capsys):
        """Test finalizing nonexistent session logs error."""
        storage_service.finalize_session(
            session_id="nonexistent",
            final_extracted=ExtractedData(),
            summary="test"
        )
        
        # Should log error but not crash
        captured = capsys.readouterr()
        assert "Cannot finalize non-existent session" in captured.out
    
    def test_load_session_with_corrupted_file(self, storage_service, tmp_path):
        """Test loading session with corrupted JSON file."""
        session_id = "corrupted-session"
        session_file = storage_service._get_session_file(session_id)
        
        # Write corrupted JSON
        with open(session_file, 'w') as f:
            f.write("{ invalid json }")
        
        # Should return None and log error
        result = storage_service.load_session(session_id)
        
        assert result is None
    
    def test_turn_includes_timestamp(self, storage_service):
        """Test that added turns include timestamp."""
        session_id = "timestamp-test"
        
        storage_service.add_turn(
            session_id=session_id,
            turn_number=1,
            user_message="Test",
            assistant_reply="Response",
            language="es",
            sentiment="neutral",
            sentiment_polarity_value=0.0,
            extracted_delta=ExtractedData()
        )
        
        session = storage_service.load_session(session_id)
        turn = session.turns[0]
        
        assert turn.timestamp is not None
        # Verify timestamp is valid ISO format
        datetime.fromisoformat(turn.timestamp)
    
    def test_session_includes_start_time(self, storage_service):
        """Test that new sessions include start_time."""
        session_id = "start-time-test"
        
        storage_service.add_turn(
            session_id=session_id,
            turn_number=1,
            user_message="Test",
            assistant_reply="Response",
            language="es",
            sentiment="neutral",
            sentiment_polarity_value=0.0,
            extracted_delta=ExtractedData()
        )
        
        session = storage_service.load_session(session_id)
        
        assert session.start_time is not None
        # Verify start_time is valid ISO format
        datetime.fromisoformat(session.start_time)


class TestStorageServiceSingleton:
    """Tests for storage service singleton pattern."""
    
    def test_get_storage_service_returns_instance(self):
        """Test that get_storage_service returns StorageService instance."""
        with patch('services.storage.settings') as mock_settings:
            mock_settings.conversation_storage_path = "/tmp/test"
            
            service = get_storage_service()
            
            assert isinstance(service, StorageService)
    
    def test_get_storage_service_singleton(self):
        """Test that get_storage_service returns same instance."""
        with patch('services.storage.settings') as mock_settings:
            mock_settings.conversation_storage_path = "/tmp/test"
            
            # Reset global service
            import services.storage
            services.storage._storage_service = None
            
            service1 = get_storage_service()
            service2 = get_storage_service()
            
            assert service1 is service2
