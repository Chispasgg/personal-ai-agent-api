"""
Unit tests for summarization.py service.
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from services.summarization import SummarizationService, get_summarization_service
from beans.schemas.extraction.extracted_data_dto import ExtractedData


class TestSummarizationService:
    """Tests for SummarizationService class."""
    
    @pytest.fixture
    def mock_chain_manager(self):
        """Fixture for mocked chain manager."""
        mock = MagicMock()
        mock.generate_summary.return_value = (
            "Cliente reporta problema con pedido ABC123456. "
            "El pedido no llegó después de 2 semanas. "
            "Categoría: envío. Urgencia: alta."
        )
        return mock
    
    @pytest.fixture
    def summarization_service(self, mock_chain_manager):
        """Fixture for summarization service with mocked chain manager."""
        with patch('services.summarization.get_chain_manager', return_value=mock_chain_manager):
            service = SummarizationService()
            return service
    
    def test_generate_summary_basic(self, summarization_service, mock_chain_manager):
        """Test basic summary generation."""
        conversation_text = """User: Hola
Assistant: ¡Hola! ¿En qué puedo ayudarte?
User: Mi pedido ABC123456 no llegó
Assistant: Entiendo, ¿cuál es la categoría?
User: Es de envío
Assistant: ¿Qué urgencia tiene?
User: Alta, lo necesito urgente"""
        
        extracted_data = ExtractedData(
            order_id="ABC123456",
            category="shipping",
            description="Pedido no llegó",
            urgency="high"
        )
        
        summary = summarization_service.generate_summary(
            conversation_text=conversation_text,
            extracted_data=extracted_data,
            language="es"
        )
        
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "ABC123456" in summary or "pedido" in summary.lower()
    
    def test_generate_summary_calls_chain_manager(self, summarization_service, mock_chain_manager):
        """Test that summary generation calls chain manager correctly."""
        conversation_text = "Test conversation"
        extracted_data = ExtractedData(order_id="ABC123")
        
        summarization_service.generate_summary(
            conversation_text=conversation_text,
            extracted_data=extracted_data,
            language="es"
        )
        
        # Verify chain manager was called
        mock_chain_manager.generate_summary.assert_called_once()
        call_args = mock_chain_manager.generate_summary.call_args
        
        assert call_args.kwargs['conversation'] == conversation_text
        assert call_args.kwargs['language'] == "es"
    
    def test_generate_summary_with_complete_data(self, summarization_service):
        """Test summary generation with complete extracted data."""
        conversation_text = "Full conversation here"
        
        extracted_data = ExtractedData(
            order_id="ABC123456",
            category="billing",
            description="Duplicate charge on credit card",
            urgency="high"
        )
        
        summary = summarization_service.generate_summary(
            conversation_text=conversation_text,
            extracted_data=extracted_data,
            language="en"
        )
        
        assert isinstance(summary, str)
        assert len(summary) > 0
    
    def test_generate_summary_with_partial_data(self, summarization_service):
        """Test summary generation with partial extracted data."""
        conversation_text = "Partial conversation"
        
        extracted_data = ExtractedData(
            order_id="ABC123",
            category=None,
            description="Some issue",
            urgency=None
        )
        
        summary = summarization_service.generate_summary(
            conversation_text=conversation_text,
            extracted_data=extracted_data,
            language="es"
        )
        
        # Should still generate summary
        assert isinstance(summary, str)
        assert len(summary) > 0
    
    def test_generate_summary_handles_exception(self, summarization_service, capsys):
        """Test that summary generation handles exceptions gracefully."""
        with patch.object(
            summarization_service.chain_manager,
            'generate_summary',
            side_effect=Exception("LLM error")
        ):
            summary = summarization_service.generate_summary(
                conversation_text="Test",
                extracted_data=ExtractedData(),
                language="es"
            )
            
            # Should return error message
            assert summary == "Error generating summary"
            
            # Should log error
            captured = capsys.readouterr()
            assert "Summarization failed" in captured.out
    
    def test_generate_summary_empty_conversation(self, summarization_service):
        """Test summary generation with empty conversation."""
        summary = summarization_service.generate_summary(
            conversation_text="",
            extracted_data=ExtractedData(),
            language="es"
        )
        
        # Should still work
        assert isinstance(summary, str)
    
    def test_generate_summary_logs_length(self, summarization_service, capsys):
        """Test that summary generation logs summary length."""
        summarization_service.generate_summary(
            conversation_text="Test conversation",
            extracted_data=ExtractedData(),
            language="es"
        )
        
        captured = capsys.readouterr()
        assert "Generated summary" in captured.out
        assert "length:" in captured.out
    
    def test_generate_summary_different_languages(self, summarization_service, mock_chain_manager):
        """Test summary generation with different languages."""
        conversation_text = "Test"
        extracted_data = ExtractedData()
        
        # Test Spanish
        summary_es = summarization_service.generate_summary(
            conversation_text=conversation_text,
            extracted_data=extracted_data,
            language="es"
        )
        assert isinstance(summary_es, str)
        
        # Test English
        summary_en = summarization_service.generate_summary(
            conversation_text=conversation_text,
            extracted_data=extracted_data,
            language="en"
        )
        assert isinstance(summary_en, str)
    
    def test_generate_summary_extracted_data_serialization(self, summarization_service, mock_chain_manager):
        """Test that extracted data is properly serialized."""
        extracted_data = ExtractedData(
            order_id="ABC123",
            category="technical",
            description="Software bug",
            urgency="medium"
        )
        
        summarization_service.generate_summary(
            conversation_text="Test",
            extracted_data=extracted_data,
            language="es"
        )
        
        # Verify that extracted_data was converted to dict
        call_args = mock_chain_manager.generate_summary.call_args
        extracted_dict = call_args.kwargs['extracted_data']
        
        assert isinstance(extracted_dict, dict)
        assert extracted_dict['order_id'] == "ABC123"
        assert extracted_dict['category'] == "technical"


class TestSummarizationServiceSingleton:
    """Tests for summarization service singleton pattern."""
    
    def test_get_summarization_service_returns_instance(self):
        """Test that get_summarization_service returns SummarizationService instance."""
        with patch('services.summarization.get_chain_manager'):
            service = get_summarization_service()
            
            assert isinstance(service, SummarizationService)
    
    def test_get_summarization_service_singleton(self):
        """Test that get_summarization_service returns same instance."""
        with patch('services.summarization.get_chain_manager'):
            # Reset global service
            import services.summarization
            services.summarization._summarization_service = None
            
            service1 = get_summarization_service()
            service2 = get_summarization_service()
            
            assert service1 is service2
