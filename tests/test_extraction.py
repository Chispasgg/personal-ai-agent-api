"""
Unit tests for extraction.py service.
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from services.extraction import ExtractionService, get_extraction_service
from beans.schemas.extraction.extracted_data_dto import ExtractedData
from beans.schemas.extraction.extraction_result_dto import ExtractionResult


class TestExtractionService:
    """Tests for ExtractionService class."""
    
    @pytest.fixture
    def mock_chain_manager(self):
        """Fixture for mocked chain manager."""
        mock = MagicMock()
        mock.extract_structured_info.return_value = {
            "order_id": "ABC123456",
            "category": "shipping",
            "description": "Pedido no llegó",
            "urgency": "high"
        }
        return mock
    
    @pytest.fixture
    def extraction_service(self, mock_chain_manager):
        """Fixture for extraction service with mocked chain manager."""
        with patch('services.extraction.get_chain_manager', return_value=mock_chain_manager):
            service = ExtractionService()
            return service
    
    def test_extract_from_message_basic(self, extraction_service, mock_chain_manager):
        """Test basic extraction from message."""
        message = "Mi pedido ABC123456 no ha llegado"
        history = ""
        
        result = extraction_service.extract_from_message(
            message=message,
            history=history,
            language="es",
            current_data=None
        )
        
        assert isinstance(result, ExtractionResult)
        assert result.extracted.order_id == "ABC123456"
        assert result.extracted.category == "shipping"
        assert result.is_complete is True
        assert len(result.missing_fields) == 0
    
    def test_extract_from_message_with_history(self, extraction_service, mock_chain_manager):
        """Test extraction with conversation history."""
        message = "Es urgente"
        history = "User: Mi pedido ABC123\nAssistant: ¿Cuál es el problema?"
        
        result = extraction_service.extract_from_message(
            message=message,
            history=history,
            language="es"
        )
        
        # Verify chain manager was called with history
        mock_chain_manager.extract_structured_info.assert_called_once_with(
            message=message,
            history=history
        )
        assert isinstance(result, ExtractionResult)
    
    def test_extract_merges_with_current_data(self, extraction_service):
        """Test extraction merges with existing data."""
        # Setup mock to return partial data
        with patch.object(
            extraction_service.chain_manager,
            'extract_structured_info',
            return_value={"category": "billing", "urgency": "high"}
        ):
            current_data = ExtractedData(
                order_id="ABC123456",
                description="Problema con factura"
            )
            
            result = extraction_service.extract_from_message(
                message="Es de facturación y urgente",
                history="",
                current_data=current_data
            )
            
            # Should merge: keep order_id and description, add category and urgency
            assert result.extracted.order_id == "ABC123456"
            assert result.extracted.description == "Problema con factura"
            assert result.extracted.category == "billing"
            assert result.extracted.urgency == "high"
    
    def test_extract_incomplete_data(self, extraction_service):
        """Test extraction with incomplete data."""
        with patch.object(
            extraction_service.chain_manager,
            'extract_structured_info',
            return_value={"order_id": "ABC123", "category": None}
        ):
            result = extraction_service.extract_from_message(
                message="Mi pedido ABC123",
                history=""
            )
            
            assert result.is_complete is False
            assert "category" in result.missing_fields
            assert "urgency" in result.missing_fields
            assert "description" in result.missing_fields
    
    def test_extract_handles_parsing_error(self, extraction_service, capsys):
        """Test extraction handles parsing errors gracefully."""
        # Return data that will cause a Pydantic validation error
        with patch.object(
            extraction_service.chain_manager,
            'extract_structured_info',
            side_effect=Exception("Parsing error")
        ):
            result = extraction_service.extract_from_message(
                message="Test message",
                history=""
            )
            
            # Should return empty ExtractedData on parsing error
            assert isinstance(result, ExtractionResult)
            assert result.is_complete is False
            
            # Should log error
            captured = capsys.readouterr()
            assert "Extraction failed" in captured.out
    
    def test_extract_handles_llm_exception(self, extraction_service, capsys):
        """Test extraction handles LLM exceptions gracefully."""
        with patch.object(
            extraction_service.chain_manager,
            'extract_structured_info',
            side_effect=Exception("LLM error")
        ):
            result = extraction_service.extract_from_message(
                message="Test message",
                history=""
            )
            
            # Should return empty result on exception
            assert isinstance(result, ExtractionResult)
            assert result.is_complete is False
            
            # Should log error
            captured = capsys.readouterr()
            assert "Extraction failed" in captured.out
    
    def test_extract_with_current_data_on_error(self, extraction_service):
        """Test extraction returns current data when LLM fails."""
        current_data = ExtractedData(
            order_id="ABC123",
            category="shipping"
        )
        
        with patch.object(
            extraction_service.chain_manager,
            'extract_structured_info',
            side_effect=Exception("LLM error")
        ):
            result = extraction_service.extract_from_message(
                message="Test",
                history="",
                current_data=current_data
            )
            
            # Should return current data on error
            assert result.extracted.order_id == "ABC123"
            assert result.extracted.category == "shipping"
    
    def test_extract_language_parameter(self, extraction_service, mock_chain_manager):
        """Test that language parameter is passed correctly."""
        result = extraction_service.extract_from_message(
            message="Test",
            history="",
            language="en"
        )
        
        # Verify extraction was called (language doesn't affect the mock call)
        mock_chain_manager.extract_structured_info.assert_called_once()
    
    def test_extract_incremental_completion(self, extraction_service):
        """Test incremental data completion over multiple extractions."""
        # First extraction: only order_id
        with patch.object(
            extraction_service.chain_manager,
            'extract_structured_info',
            return_value={"order_id": "ABC123"}
        ):
            result1 = extraction_service.extract_from_message(
                message="Mi pedido ABC123",
                history=""
            )
            
            assert result1.is_complete is False
            current_data = result1.extracted
        
        # Second extraction: add category
        with patch.object(
            extraction_service.chain_manager,
            'extract_structured_info',
            return_value={"category": "shipping"}
        ):
            result2 = extraction_service.extract_from_message(
                message="Es de envío",
                history="User: Mi pedido ABC123",
                current_data=current_data
            )
            
            assert result2.extracted.order_id == "ABC123"
            assert result2.extracted.category == "shipping"
            assert result2.is_complete is False
        
        # Third extraction: add description and urgency
        with patch.object(
            extraction_service.chain_manager,
            'extract_structured_info',
            return_value={"description": "No llegó el pedido", "urgency": "high"}
        ):
            result3 = extraction_service.extract_from_message(
                message="No llegó y es urgente",
                history="...",
                current_data=result2.extracted
            )
            
            assert result3.extracted.order_id == "ABC123"
            assert result3.extracted.category == "shipping"
            assert result3.extracted.description == "No llegó el pedido"
            assert result3.extracted.urgency == "high"
            assert result3.is_complete is True
    
    def test_extract_empty_message(self, extraction_service):
        """Test extraction with empty message."""
        result = extraction_service.extract_from_message(
            message="",
            history=""
        )
        
        # Should handle gracefully
        assert isinstance(result, ExtractionResult)


class TestExtractionServiceSingleton:
    """Tests for extraction service singleton pattern."""
    
    def test_get_extraction_service_returns_instance(self):
        """Test that get_extraction_service returns ExtractionService instance."""
        with patch('services.extraction.get_chain_manager'):
            service = get_extraction_service()
            
            assert isinstance(service, ExtractionService)
    
    def test_get_extraction_service_singleton(self):
        """Test that get_extraction_service returns same instance."""
        with patch('services.extraction.get_chain_manager'):
            # Reset global service
            import services.extraction
            services.extraction._extraction_service = None
            
            service1 = get_extraction_service()
            service2 = get_extraction_service()
            
            assert service1 is service2
