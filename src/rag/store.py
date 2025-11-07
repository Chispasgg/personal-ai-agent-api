"""
FAISS vector store management.
"""
from pathlib import Path
from typing import Optional
from langchain_community.vectorstores import FAISS
from langchain.embeddings.base import Embeddings
from config.settings import settings


class VectorStoreManager:
    """Manages FAISS vector store persistence."""

    def __init__(self):
        """Initialize vector store manager."""
        self.store_path = Path(settings.vectorstore_path)
        self.index_name = settings.vectorstore_index_name
        self.store_path.mkdir(parents=True, exist_ok=True)

    def save_vectorstore(self, vectorstore: FAISS) -> None:
        """
        Save FAISS vectorstore to disk.

        Args:
            vectorstore: FAISS vectorstore instance
        """
        try:
            full_path = self.store_path / self.index_name
            vectorstore.save_local(str(full_path))
            print(f"Saved vectorstore, path: {str(full_path)}")
        except Exception as e:
            print(f"Failed to save vectorstore, error: {str(e)}")
            raise

    def load_vectorstore(self, embeddings: Embeddings) -> Optional[FAISS]:
        """
        Load FAISS vectorstore from disk.

        Args:
            embeddings: Embeddings model to use

        Returns:
            FAISS vectorstore or None if not found
        """
        try:
            full_path = self.store_path / self.index_name

            if not full_path.exists():
                print(f"Vectorstore not found, path: {str(full_path)}")
                return None

            vectorstore = FAISS.load_local(
                str(full_path),
                embeddings,
                allow_dangerous_deserialization=True
            )
            print(f"Loaded vectorstore, path: {str(full_path)}")
            return vectorstore

        except Exception as e:
            print(f"Failed to load vectorstore, error: {str(e)}")
            return None

    def exists(self) -> bool:
        """
        Check if vectorstore exists on disk.

        Returns:
            True if vectorstore exists
        """
        full_path = self.store_path / self.index_name
        return full_path.exists()


# Global vector store manager
_store_manager: Optional[VectorStoreManager] = None


def get_vector_store_manager() -> VectorStoreManager:
    """Get global vector store manager instance."""
    global _store_manager
    if _store_manager is None:
        _store_manager = VectorStoreManager()
    return _store_manager
