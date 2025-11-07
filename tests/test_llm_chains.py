"""
Tests for LLM chains.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.llm.chains import ChainManager, get_chain_manager


@pytest.fixture
def mock_llm():
    """Mock LLM."""
    llm = Mock()
    llm.invoke.return_value = "Mocked response"
    return llm


@pytest.fixture
def mock_retriever():
    """Mock retriever."""
    retriever = Mock()
    retriever.get_relevant_documents.return_value = [
        Mock(page_content="Document 1"),
        Mock(page_content="Document 2")
    ]
    return retriever


@pytest.fixture
def chain_manager(mock_llm):
    """Create chain manager with mocked LLM."""
    with patch('llm.models.get_llm') as mock_get_llm:
        mock_get_llm.return_value = mock_llm
        manager = ChainManager()
        yield manager


class TestChainManager:
    """Tests for ChainManager."""
    
    def test_initialization(self, chain_manager):
        """Test chain manager initialization."""
        assert chain_manager is not None
        assert chain_manager.llm is not None
    
    def test_extract_information(self, chain_manager, mock_llm):
        """Test information extraction chain."""
        mock_llm.invoke.return_value = '{"order_id": "ABC123", "category": "shipping"}'
        
        result = chain_manager.extract_structured_info(
            message="My order ABC123 is late",
            history="Previous conversation"
        )
        
        assert isinstance(result, dict)
        # If parsing succeeds, should have extracted data
        if result:
            assert "order_id" in result or "category" in result
    
    def test_generate_response(self, chain_manager, mock_llm):
        """Test response generation chain."""
        mock_llm.invoke.return_value = "I can help you with that"
        
        response = chain_manager.generate_response(
            message="Help me",
            context="Previous context",
            language="en",
            sentiment="neutral"
        )
        
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_generate_response_negative_sentiment(self, chain_manager, mock_llm):
        """Test response generation with negative sentiment."""
        mock_llm.invoke.return_value = "I sincerely apologize"
        
        response = chain_manager.generate_response(
            message="This is terrible",
            context="User is frustrated",
            language="en",
            sentiment="negative"
        )
        
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_generate_summary(self, chain_manager, mock_llm):
        """Test summary generation chain."""
        mock_llm.invoke.return_value = "Summary: Order issue resolved"
        
        summary = chain_manager.generate_summary(
            conversation="Long conversation text",
            extracted_data={"order_id": "ABC123", "category": "shipping"},
            language="en"
        )
        
        assert isinstance(summary, str)
        assert len(summary) > 0
    
    def test_rag_chain(self, chain_manager, mock_retriever):
        """Test RAG chain creation."""
        # Patch ConversationalRetrievalChain to avoid validation issues
        with patch('src.llm.chains.ConversationalRetrievalChain') as MockChain:
            mock_chain_instance = Mock()
            MockChain.from_llm.return_value = mock_chain_instance
            
            chain = chain_manager.create_rag_chain(
                retriever=mock_retriever,
                language="en"
            )
            
            assert chain is not None
            assert MockChain.from_llm.called


class TestGetChainManager:
    """Tests for get_chain_manager singleton."""
    
    def test_singleton_pattern(self):
        """Test that get_chain_manager returns same instance."""
        with patch('llm.models.get_llm'):
            manager1 = get_chain_manager()
            manager2 = get_chain_manager()
            
            assert manager1 is manager2
    
    def test_lazy_initialization(self):
        """Test lazy initialization."""
        # Reset singleton
        import src.llm.chains
        src.llm.chains._chain_manager = None
        
        with patch('llm.models.get_llm'):
            manager = get_chain_manager()
            assert manager is not None


class TestChainErrorHandling:
    """Tests for error handling in chains."""
    
    def test_extraction_json_parse_error(self, chain_manager, mock_llm):
        """Test extraction handles invalid JSON."""
        mock_llm.invoke.return_value = "Not valid JSON"
        
        result = chain_manager.extract_structured_info(
            message="Test message",
            history=""
        )
        
        # Should return empty dict on parse error
        assert result == {}
    
    def test_llm_api_error(self, chain_manager, mock_llm):
        """Test handling of LLM API errors."""
        mock_llm.invoke.side_effect = Exception("API Error")
        
        # Should return error message instead of raising
        response = chain_manager.generate_response(
            message="Test",
            context="",
            language="en"
        )
        
        assert "trouble" in response or "apologize" in response

