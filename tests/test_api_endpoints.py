"""
Tests for API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from src.server.server import create_app
from src.beans.schemas.conversations.chat_request_dto import ChatRequest
from src.beans.schemas.conversations.chat_response_dto import ChatResponse
from src.beans.schemas.extraction.extracted_data_dto import ExtractedData


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def mock_conversation_service():
    """Mock conversation service."""
    # Mock at the point where it's imported in the endpoint
    with patch('routes.chat.v1.ep_chat.get_conversation_service') as mock_get_service:
        service = Mock()
        # Make process_message async and return the mock_response attribute
        async def mock_process_message(request):
            return service.mock_response
        service.process_message = mock_process_message
        mock_get_service.return_value = service
        yield service


class TestHealthEndpoint:
    """Tests for health endpoint."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data


class TestChatEndpoint:
    """Tests for chat endpoint."""
    
    def test_chat_success(self, client, mock_conversation_service):
        """Test successful chat interaction."""
        # Setup mock response as a dict to avoid Pydantic validation issues
        mock_response_dict = {
            "reply": "Test reply",
            "sound_file_base64": None,
            "language": "es",
            "sentiment": "neutral",
            "extracted": {
                "order_id": None,
                "category": None,
                "description": None,
                "urgency": None
            },
            "missing_fields": ["order_id", "category", "description", "urgency"],
            "summary_ready": False,
            "summary": None,
            "session_id": "test-123",
            "turn_number": 1
        }
        
        # Create actual ChatResponse from dict and set it on mock
        mock_response = ChatResponse(**mock_response_dict)
        mock_conversation_service.mock_response = mock_response
        
        # Make request
        response = client.post(
            "/api/v1/chat",
            json={
                "session_id": "test-123",
                "message": "Hola"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["reply"] == "Test reply"
        assert data["session_id"] == "test-123"
        assert data["turn_number"] == 1
    
    def test_chat_with_extraction(self, client, mock_conversation_service):
        """Test chat with extracted data."""
        mock_response = ChatResponse(
            reply="I understand",
            sound_file_base64=None,
            language="en",
            sentiment="negative",
            extracted={
                "order_id": "ABC123456",
                "category": "shipping",
                "description": "Order not arrived",
                "urgency": "high"
            },
            missing_fields=[],
            summary_ready=True,
            summary="Summary text",
            session_id="test-456",
            turn_number=5
        )
        mock_conversation_service.mock_response = mock_response
        
        response = client.post(
            "/api/v1/chat",
            json={
                "session_id": "test-456",
                "message": "My order ABC123456 hasn't arrived"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["extracted"]["order_id"] == "ABC123456"
        assert data["summary_ready"] is True
        assert data["summary"] == "Summary text"
    
    def test_chat_invalid_request(self, client):
        """Test chat with invalid request."""
        response = client.post(
            "/api/v1/chat",
            json={"message": "Test"}  # Missing session_id
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_chat_empty_message(self, client):
        """Test chat with empty message."""
        response = client.post(
            "/api/v1/chat",
            json={
                "session_id": "test-123",
                "message": ""
            }
        )
        
        assert response.status_code == 422
    
    def test_chat_with_audio_response(self, client, mock_conversation_service):
        """Test chat with audio response requested."""
        mock_response = ChatResponse(
            reply="Test reply",
            sound_file_base64="base64encodedaudio",
            language="es",
            sentiment="neutral",
            extracted={
                "order_id": None,
                "category": None,
                "description": None,
                "urgency": None
            },
            missing_fields=["order_id"],
            summary_ready=False,
            summary=None,
            session_id="test-789",
            turn_number=1
        )
        mock_conversation_service.mock_response = mock_response
        
        response = client.post(
            "/api/v1/chat",
            json={
                "session_id": "test-789",
                "message": "Hello",
                "audio_response": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["sound_file_base64"] == "base64encodedaudio"


class TestAdminEndpoints:
    """Tests for admin endpoints."""
    
    @pytest.fixture
    def admin_headers(self):
        """Admin API key headers."""
        return {"X-API-Key": "test-admin-key"}
    
    @patch('routes.admin.utils.admin_utils.settings')
    @patch('routes.admin.v1.ep_admin.ingest_knowledge_base')
    def test_ingest_success(self, mock_ingest, mock_settings, client, admin_headers):
        """Test successful knowledge base ingestion."""
        mock_settings.api_key_admin = "test-admin-key"
        # Mock ingest to do nothing (it returns None in real code)
        mock_ingest.return_value = None
        
        response = client.post(
            "/api/v1/admin/ingest",
            json={"kb_path": "../kb"},
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "message" in data
    
    @patch('routes.admin.utils.admin_utils.settings')
    def test_ingest_unauthorized(self, mock_settings, client):
        """Test ingestion without API key."""
        mock_settings.api_key_admin = "test-admin-key"
        
        response = client.post(
            "/api/v1/admin/ingest",
            json={"kb_path": "../kb"}
        )
        
        assert response.status_code == 401
    
    @patch('routes.admin.utils.admin_utils.settings')
    def test_ingest_wrong_api_key(self, mock_settings, client):
        """Test ingestion with wrong API key."""
        mock_settings.api_key_admin = "correct-key"
        
        response = client.post(
            "/api/v1/admin/ingest",
            json={"kb_path": "../kb"},
            headers={"X-API-Key": "wrong-key"}
        )
        
        assert response.status_code == 401
    
    @patch('routes.admin.utils.admin_utils.settings')
    @patch('services.storage.get_storage_service')
    def test_get_session_success(self, mock_storage, mock_settings, client, admin_headers):
        """Test getting session data."""
        mock_settings.api_key_admin = "test-admin-key"
        
        mock_session = {
            "session_id": "test-123",
            "turns": [],
            "final_extracted": {},
            "summary": None
        }
        mock_storage.return_value.load_session.return_value = mock_session
        
        response = client.get(
            "/api/v1/admin/session/test-123",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == "test-123"
    
    @patch('routes.admin.utils.admin_utils.settings')
    @patch('services.storage.get_storage_service')
    def test_get_session_not_found(self, mock_storage, mock_settings, client, admin_headers):
        """Test getting non-existent session."""
        mock_settings.api_key_admin = "test-admin-key"
        mock_storage.return_value.load_session.return_value = None
        
        response = client.get(
            "/api/v1/admin/session/nonexistent",
            headers=admin_headers
        )
        
        assert response.status_code == 404


class TestCORSMiddleware:
    """Tests for CORS middleware."""
    
    def test_cors_headers_present(self, client):
        """Test that CORS headers are present."""
        response = client.options(
            "/api/v1/health",
            headers={"Origin": "http://localhost:3000"}
        )
        
        assert "access-control-allow-origin" in response.headers


class TestErrorHandling:
    """Tests for error handling."""
    
    def test_internal_server_error(self, client):
        """Test internal server error handling."""
        # Mock the service to raise an exception
        with patch('routes.chat.v1.ep_chat.get_conversation_service') as mock_get_service:
            service = Mock()
            
            async def mock_error(request):
                raise Exception("Test error")
            
            service.process_message = mock_error
            mock_get_service.return_value = service
            
            response = client.post(
                "/api/v1/chat",
                json={
                    "session_id": "test-123",
                    "message": "Test"
                }
            )
            
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
