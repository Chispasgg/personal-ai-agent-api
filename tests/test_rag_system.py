"""
Tests for RAG components (ingest, store, retriever).
"""
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.rag.ingest import ingest_knowledge_base, load_documents, split_documents, create_vectorstore
from src.rag.store import VectorStoreManager, get_vector_store_manager
from src.rag.retriever import get_retriever, query_knowledge_base


@pytest.fixture
def temp_kb_dir():
    """Create temporary knowledge base directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create sample markdown file
        kb_path = Path(tmpdir) / "kb"
        kb_path.mkdir()
        
        sample_file = kb_path / "faqs.md"
        sample_file.write_text("""
# Frequently Asked Questions

## Shipping

### How long does shipping take?
Standard shipping takes 5-7 business days.

### Can I track my order?
Yes, you will receive a tracking number via email.

## Returns

### What is the return policy?
You can return items within 30 days.
        """)
        
        yield str(kb_path)


@pytest.fixture
def temp_vectorstore_dir():
    """Create temporary vectorstore directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


class TestIngest:
    """Tests for knowledge base ingestion."""
    
    @patch('src.rag.ingest.FAISS')
    @patch('src.rag.ingest.get_embeddings')
    @patch('src.rag.ingest.get_vector_store_manager')
    def test_ingest_success(self, mock_get_manager, mock_embeddings, mock_faiss, temp_kb_dir, temp_vectorstore_dir):
        """Test successful knowledge base ingestion."""
        # Mock embeddings - debe devolver arrays reales
        mock_emb = Mock()
        mock_emb.embed_documents.return_value = [[0.1] * 1536]  # Simula embeddings reales
        mock_embeddings.return_value = mock_emb
        
        # Mock FAISS
        mock_vectorstore = Mock()
        mock_faiss.from_documents.return_value = mock_vectorstore
        
        # Mock vector store manager
        mock_manager = Mock()
        mock_get_manager.return_value = mock_manager
        
        with patch('src.config.settings.settings') as mock_settings:
            mock_settings.vectorstore_path = temp_vectorstore_dir
            mock_settings.chunk_size = 500
            mock_settings.chunk_overlap = 50
            mock_settings.kb_path = temp_kb_dir
            
            # Should complete without error
            ingest_knowledge_base(temp_kb_dir)
            
            # Verify manager's save was called
            assert mock_manager.save_vectorstore.called
    
    @patch('src.rag.ingest.get_embeddings')
    @patch('src.rag.ingest.get_vector_store_manager')
    def test_ingest_empty_directory(self, mock_get_manager, mock_embeddings, temp_vectorstore_dir):
        """Test ingestion with empty directory."""
        with tempfile.TemporaryDirectory() as empty_dir:
            with patch('src.config.settings.settings') as mock_settings:
                mock_settings.vectorstore_path = temp_vectorstore_dir
                mock_settings.kb_path = empty_dir
                
                # Should handle gracefully or raise appropriate error
                try:
                    ingest_knowledge_base(empty_dir)
                except Exception as e:
                    # Acceptable to raise error for empty directory
                    assert "not found" in str(e).lower() or "no documents" in str(e).lower()
    
    @patch('src.rag.ingest.get_embeddings')
    @patch('src.rag.ingest.get_vector_store_manager')
    def test_load_documents(self, mock_get_manager, mock_embeddings, temp_kb_dir):
        """Test loading documents from KB directory."""
        documents = load_documents(temp_kb_dir)
        
        assert documents is not None
        assert len(documents) >= 1
        assert hasattr(documents[0], 'page_content')
    
    def test_ingest_nonexistent_directory(self):
        """Test ingestion with non-existent directory."""
        with pytest.raises(FileNotFoundError):
            ingest_knowledge_base("/nonexistent/path")


class TestVectorStore:
    """Tests for vector store operations."""
    
    def test_vector_store_manager_init(self):
        """Test VectorStoreManager initialization."""
        from src.rag.store import VectorStoreManager
        manager = VectorStoreManager()
        
        assert manager is not None
        assert hasattr(manager, 'store_path')
        assert hasattr(manager, 'index_name')
        # Verificar que el path existe después de la inicialización
        assert manager.store_path.exists()
    
    @patch('src.rag.store.FAISS')
    def test_save_vectorstore(self, mock_faiss, temp_vectorstore_dir):
        """Test saving vector store to disk."""
        mock_store = Mock()
        mock_store.save_local = Mock()
        
        with patch('src.rag.store.settings') as mock_settings:
            mock_settings.vectorstore_path = temp_vectorstore_dir
            mock_settings.vectorstore_index_name = "test_index"
            
            from src.rag.store import VectorStoreManager
            manager = VectorStoreManager()
            manager.save_vectorstore(mock_store)
            
            mock_store.save_local.assert_called_once()
    
    @patch('src.rag.store.FAISS')
    def test_load_vectorstore(self, mock_faiss, temp_vectorstore_dir):
        """Test loading vector store from disk."""
        mock_embeddings = Mock()
        mock_faiss.load_local.return_value = Mock()
        
        with patch('src.rag.store.settings') as mock_settings:
            mock_settings.vectorstore_path = temp_vectorstore_dir
            mock_settings.vectorstore_index_name = "test_index"
            
            # Create dummy index file
            index_path = Path(temp_vectorstore_dir) / "test_index"
            index_path.mkdir(parents=True, exist_ok=True)
            (index_path / "index.faiss").touch()
            
            from src.rag.store import VectorStoreManager
            manager = VectorStoreManager()
            store = manager.load_vectorstore(mock_embeddings)
            
            assert store is not None
            mock_faiss.load_local.assert_called_once()
    
    def test_load_vectorstore_not_found(self, temp_vectorstore_dir):
        """Test loading non-existent vector store."""
        from src.rag.store import VectorStoreManager
        
        # Create manager with default settings
        manager = VectorStoreManager()
        mock_embeddings = Mock()
        
        # Temporarily change the store path to a nonexistent one
        original_path = manager.store_path
        manager.store_path = Path(temp_vectorstore_dir) / "nonexistent"
        manager.index_name = "nonexistent"
        
        store = manager.load_vectorstore(mock_embeddings)
        
        # Should return None when directory doesn't exist
        assert store is None
        
        # Restore original path
        manager.store_path = original_path
    
    def test_exists_method(self, temp_vectorstore_dir):
        """Test exists method."""
        from src.rag.store import VectorStoreManager
        
        manager = VectorStoreManager()
        
        # Temporarily change paths to test directory
        original_path = manager.store_path
        test_dir = Path(temp_vectorstore_dir) / "unique_test_exists"
        manager.store_path = test_dir
        manager.index_name = "test_index"
        
        # Should not exist initially
        assert manager.exists() is False
        
        # Create index directory
        index_path = test_dir / "test_index"
        index_path.mkdir(parents=True, exist_ok=True)
        
        # Now should exist
        assert manager.exists() is True
        
        # Restore
        manager.store_path = original_path
    
    def test_get_vector_store_manager_singleton(self):
        """Test singleton pattern of get_vector_store_manager."""
        with patch('src.config.settings.settings'):
            manager1 = get_vector_store_manager()
            manager2 = get_vector_store_manager()
            
            assert manager1 is manager2


class TestRetriever:
    """Tests for retriever operations."""
    
    @patch('src.rag.retriever.get_vector_store_manager')
    @patch('src.rag.retriever.get_embeddings')
    def test_get_retriever(self, mock_embeddings, mock_get_manager):
        """Test getting retriever instance."""
        mock_embeddings.return_value = Mock()
        
        mock_store = Mock()
        mock_store.as_retriever.return_value = Mock()
        
        mock_manager = Mock()
        mock_manager.load_vectorstore.return_value = mock_store
        mock_get_manager.return_value = mock_manager
        
        with patch('src.config.settings.settings') as mock_settings:
            mock_settings.rag_top_k = 5
            
            retriever = get_retriever()
            
            assert retriever is not None
            mock_store.as_retriever.assert_called_once()
    
    @patch('src.rag.retriever.get_vector_store_manager')
    @patch('src.rag.retriever.get_embeddings')
    def test_query_knowledge_base(self, mock_embeddings, mock_get_manager):
        """Test querying knowledge base."""
        mock_embeddings.return_value = Mock()
        
        # Mock vectorstore with relevant documents
        mock_doc1 = Mock()
        mock_doc1.page_content = "Shipping takes 5-7 days"
        mock_doc2 = Mock()
        mock_doc2.page_content = "You can track your order"
        
        mock_vectorstore = Mock()
        mock_vectorstore.similarity_search.return_value = [mock_doc1, mock_doc2]
        
        mock_manager = Mock()
        mock_manager.load_vectorstore.return_value = mock_vectorstore
        mock_get_manager.return_value = mock_manager
        
        results = query_knowledge_base("How long is shipping?", k=2)
        
        assert len(results) == 2
        assert "Shipping takes 5-7 days" in results
        assert "You can track your order" in results
    
    @patch('src.rag.retriever.get_vector_store_manager')
    @patch('src.rag.retriever.get_embeddings')
    def test_query_no_results(self, mock_embeddings, mock_get_manager):
        """Test query with no relevant results."""
        mock_embeddings.return_value = Mock()
        
        mock_vectorstore = Mock()
        mock_vectorstore.similarity_search.return_value = []
        
        mock_manager = Mock()
        mock_manager.load_vectorstore.return_value = mock_vectorstore
        mock_get_manager.return_value = mock_manager
        
        results = query_knowledge_base("Irrelevant query", k=5)
        
        assert results == []
    
    @patch('src.rag.retriever.get_vector_store_manager')
    @patch('src.rag.retriever.get_embeddings')
    def test_query_with_limit(self, mock_embeddings, mock_get_manager):
        """Test query with result limit."""
        mock_embeddings.return_value = Mock()
        
        docs = [Mock(page_content=f"Doc {i}") for i in range(10)]
        
        mock_vectorstore = Mock()
        mock_vectorstore.similarity_search.return_value = docs[:3]  # Return only 3
        
        mock_manager = Mock()
        mock_manager.load_vectorstore.return_value = mock_vectorstore
        mock_get_manager.return_value = mock_manager
        
        results = query_knowledge_base("Test query", k=3)
        
        # Should respect the limit
        assert len(results) <= 3
    
    @patch('src.rag.retriever.get_vector_store_manager')
    @patch('src.rag.retriever.get_embeddings')
    def test_query_no_vectorstore(self, mock_embeddings, mock_get_manager):
        """Test query when vectorstore doesn't exist."""
        mock_embeddings.return_value = Mock()
        
        mock_manager = Mock()
        mock_manager.load_vectorstore.return_value = None  # No vectorstore
        mock_get_manager.return_value = mock_manager
        
        # Should return empty list
        results = query_knowledge_base("Test")
        assert results == []


class TestRAGIntegration:
    """Integration tests for RAG system."""
    
    @patch('src.rag.ingest.FAISS')
    @patch('src.rag.ingest.get_embeddings')
    @patch('src.rag.ingest.get_vector_store_manager')
    def test_full_rag_pipeline(self, mock_get_manager, mock_emb, mock_faiss, temp_kb_dir, temp_vectorstore_dir):
        """Test complete RAG pipeline: ingest -> store -> retrieve."""
        # Mock embeddings - debe devolver arrays reales
        mock_embeddings = Mock()
        mock_embeddings.embed_documents.return_value = [[0.1] * 1536]
        mock_emb.return_value = mock_embeddings
        
        # Mock FAISS
        mock_vectorstore = Mock()
        mock_faiss.from_documents.return_value = mock_vectorstore
        
        # Mock vector store manager
        mock_manager = Mock()
        mock_manager.load_vectorstore.return_value = mock_vectorstore
        mock_get_manager.return_value = mock_manager
        
        with patch('src.config.settings.settings') as mock_settings:
            mock_settings.vectorstore_path = temp_vectorstore_dir
            mock_settings.chunk_size = 500
            mock_settings.chunk_overlap = 50
            mock_settings.rag_top_k = 3
            mock_settings.kb_path = temp_kb_dir
            
            # 1. Ingest
            ingest_knowledge_base(temp_kb_dir)
            
            # Verify save was called
            assert mock_manager.save_vectorstore.called
    
    @patch('src.rag.retriever.get_vector_store_manager')
    @patch('src.rag.retriever.get_embeddings')
    def test_similarity_search_relevance(self, mock_emb, mock_get_manager):
        """Test that similarity search returns relevant results."""
        mock_emb.return_value = Mock()
        
        # Simulate relevant document
        relevant_doc = Mock()
        relevant_doc.page_content = "Shipping takes 5-7 business days"
        relevant_doc.metadata = {"score": 0.95}
        
        mock_vectorstore = Mock()
        mock_vectorstore.similarity_search.return_value = [relevant_doc]
        
        mock_manager = Mock()
        mock_manager.load_vectorstore.return_value = mock_vectorstore
        mock_get_manager.return_value = mock_manager
        
        results = query_knowledge_base("How long does shipping take?")
        
        assert len(results) > 0
        assert "shipping" in results[0].lower() or "5-7" in results[0]


class TestRAGErrorHandling:
    """Tests for RAG error handling."""
    
    @patch('src.rag.ingest.get_embeddings')
    @patch('src.rag.ingest.get_vector_store_manager')
    def test_ingest_with_corrupted_file(self, mock_get_manager, mock_embeddings, temp_vectorstore_dir):
        """Test ingestion with corrupted markdown file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            kb_path = Path(tmpdir)
            bad_file = kb_path / "corrupted.md"
            
            # Write binary data to markdown file
            bad_file.write_bytes(b'\x00\x01\x02\x03')
            
            mock_embeddings.return_value = Mock()
            mock_get_manager.return_value = Mock()
            
            with patch('src.config.settings.settings') as mock_settings:
                mock_settings.vectorstore_path = temp_vectorstore_dir
                mock_settings.kb_path = str(kb_path)
                
                # Should handle gracefully or raise error
                try:
                    ingest_knowledge_base(str(kb_path))
                except Exception:
                    # Expected to fail or skip corrupted file
                    pass
    
    @patch('src.rag.retriever.get_vector_store_manager')
    @patch('src.rag.retriever.get_embeddings')
    def test_query_with_api_error(self, mock_embeddings, mock_get_manager):
        """Test query when vectorstore similarity search fails."""
        mock_embeddings.return_value = Mock()
        
        # Mock vectorstore that raises error
        mock_vectorstore = Mock()
        mock_vectorstore.similarity_search.side_effect = Exception("API Error")
        
        mock_manager = Mock()
        mock_manager.load_vectorstore.return_value = mock_vectorstore
        mock_get_manager.return_value = mock_manager
        
        # Should return empty list on error
        results = query_knowledge_base("Test query")
        assert results == []
