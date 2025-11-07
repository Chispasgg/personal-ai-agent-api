"""
Pytest configuration and shared fixtures.
"""
import sys
import os
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock
from datetime import datetime

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def temp_storage_path(tmp_path):
    """Fixture for temporary storage path."""
    storage_dir = tmp_path / "conversations"
    storage_dir.mkdir(exist_ok=True)
    return storage_dir


@pytest.fixture
def temp_vectorstore_path(tmp_path):
    """Fixture for temporary vectorstore path."""
    vector_dir = tmp_path / "vectorstore"
    vector_dir.mkdir(exist_ok=True)
    return vector_dir


@pytest.fixture
def sample_session_id():
    """Fixture for consistent session ID."""
    return "test-session-123"


@pytest.fixture
def sample_order_id():
    """Fixture for valid order ID."""
    return "ABC123456"


@pytest.fixture
def sample_user_message():
    """Fixture for sample user message."""
    return "Mi pedido ABC123456 no ha llegado y es urgente"


@pytest.fixture
def sample_extracted_data():
    """Fixture for sample extracted data."""
    from beans.schemas.extraction.extracted_data_dto import ExtractedData
    return ExtractedData(
        order_id="ABC123456",
        category="shipping",
        description="Pedido no ha llegado",
        urgency="high"
    )


@pytest.fixture
def sample_conversation_turn():
    """Fixture for sample conversation turn."""
    from beans.schemas.conversations.conversation_turn_dto import ConversationTurn
    from beans.schemas.extraction.extracted_data_dto import ExtractedData
    
    return ConversationTurn(
        turn_number=1,
        timestamp=datetime.utcnow().isoformat(),
        user_message="Hola, necesito ayuda",
        assistant_reply="¡Hola! Estaré encantado de ayudarte.",
        language="es",
        sentiment="neutral",
        sentiment_polarity_value=0.0,
        extracted_delta=ExtractedData()
    )


@pytest.fixture
def sample_conversation_session(sample_session_id, sample_conversation_turn):
    """Fixture for sample conversation session."""
    from beans.schemas.conversations.conversation_session_dto import ConversationSession
    
    return ConversationSession(
        session_id=sample_session_id,
        start_time=datetime.utcnow().isoformat(),
        language="es",
        turns=[sample_conversation_turn],
        total_turns=1
    )


@pytest.fixture
def mock_llm_chain():
    """Fixture for mocked LLM chain."""
    mock = MagicMock()
    mock.invoke.return_value = "Mocked LLM response"
    return mock


@pytest.fixture
def mock_chain_manager():
    """Fixture for mocked chain manager."""
    from unittest.mock import MagicMock
    
    mock = MagicMock()
    mock.extract_structured_info.return_value = {
        "order_id": "ABC123456",
        "category": "shipping",
        "description": "Pedido no llegó",
        "urgency": "high"
    }
    mock.generate_response.return_value = "Respuesta generada por el mock"
    mock.generate_summary.return_value = "Resumen generado por el mock"
    
    return mock


@pytest.fixture
def mock_embeddings():
    """Fixture for mocked embeddings."""
    mock = MagicMock()
    mock.embed_query.return_value = [0.1] * 1536  # Simulated embedding vector
    mock.embed_documents.return_value = [[0.1] * 1536]
    return mock


@pytest.fixture
def mock_vectorstore():
    """Fixture for mocked vector store."""
    mock = MagicMock()
    mock.similarity_search.return_value = [
        type('Document', (), {'page_content': 'Mocked document content', 'metadata': {}})()
    ]
    mock.similarity_search_with_score.return_value = [
        (type('Document', (), {'page_content': 'Mocked document', 'metadata': {}})(), 0.9)
    ]
    return mock


@pytest.fixture(autouse=True)
def reset_global_services():
    """Reset global service instances between tests."""
    import importlib
    
    # List of modules with global service instances
    service_modules = [
        'services.conversation',
        'services.extraction',
        'services.storage',
        'services.summarization',
        'llm.memory',
        'llm.chains',
    ]
    
    # Reset global variables in each module
    for module_name in service_modules:
        try:
            if module_name in sys.modules:
                module = sys.modules[module_name]
                # Reset common global variable names
                for var in ['_conversation_service', '_extraction_service', '_storage_service',
                           '_summarization_service', '_memory_manager', '_chain_manager']:
                    if hasattr(module, var):
                        setattr(module, var, None)
        except Exception:
            pass
    
    yield
    
    # Clean up after test
    for module_name in service_modules:
        try:
            if module_name in sys.modules:
                module = sys.modules[module_name]
                for var in ['_conversation_service', '_extraction_service', '_storage_service',
                           '_summarization_service', '_memory_manager', '_chain_manager']:
                    if hasattr(module, var):
                        setattr(module, var, None)
        except Exception:
            pass


@pytest.fixture
def mock_settings(monkeypatch):
    """Fixture to mock settings."""
    class MockSettings:
        app_env = "test"
        log_level = "ERROR"
        llm_provider = "openai"
        llm_model = "gpt-4o-mini"
        conversation_storage_path = "/tmp/test_conversations"
        vectorstore_path = "/tmp/test_vectorstore"
        max_conversation_turns = 50
        sentiment_threshold_negative = -0.3
        sentiment_threshold_positive = 0.3
        default_language = "es"
        supported_languages = "es,en"
        
        @property
        def supported_languages_list(self):
            return ["es", "en"]
    
    mock = MockSettings()
    monkeypatch.setattr("config.settings.settings", mock)
    return mock
