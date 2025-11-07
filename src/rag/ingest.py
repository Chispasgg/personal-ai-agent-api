"""
Document ingestion and FAISS index creation.
"""
from pathlib import Path
from typing import List
from langchain_community.document_loaders import DirectoryLoader, TextLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
# from langchain.schema import Document
from config.settings import settings
from llm.models import get_embeddings
from rag.store import get_vector_store_manager
from langchain_core.documents.base import Document
from langchain_text_splitters.character import RecursiveCharacterTextSplitter


def load_documents(kb_path: str=settings.kb_path) -> List[Document]:
    """
    Load documents from knowledge base directory.

    Args:
        kb_path: Path to knowledge base directory

    Returns:
        List of loaded documents
    """
    kb_dir = Path(kb_path)

    if not kb_dir.exists():
        print(f"Knowledge base directory not found, path: {kb_path}")
        raise FileNotFoundError(f"KB directory not found: {kb_path}")

    print(f"Loading documents from KB, path: {kb_path}")

    # Load markdown files
    loader = DirectoryLoader(
        kb_path,
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )

    documents = loader.load()
    print(f"Loaded documents, count: {len(documents)}")

    return documents


def split_documents(documents: List[Document]) -> List[Document]:
    """
    Split documents into chunks.

    Args:
        documents: List of documents

    Returns:
        List of document chunks
    """
    print("Splitting documents into chunks")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )

    chunks = text_splitter.split_documents(documents)
    print(f"Created document chunks, count: {len(chunks)}")

    return chunks


def create_vectorstore(chunks: List[Document]) -> FAISS:
    """
    Create FAISS vectorstore from document chunks.

    Args:
        chunks: Document chunks

    Returns:
        FAISS vectorstore
    """
    print("Creating FAISS vectorstore")

    embeddings = get_embeddings()
    vectorstore = FAISS.from_documents(chunks, embeddings)

    print(f"Created vectorstore, num_vectors: {len(chunks)}")

    return vectorstore


def ingest_knowledge_base(kb_path: str=settings.kb_path) -> None:
    """
    Complete ingestion pipeline: load, split, embed, and save.

    Args:
        kb_path: Path to knowledge base directory
    """

    # Check if kb_path exists
    try:
        kb_dir = Path(kb_path)
        if not kb_dir.exists() or not kb_dir.is_dir():
            kb_path = settings.kb_path
    except Exception:
        kb_path = settings.kb_path

    print(f"Starting knowledge base ingestion, kb_path: {kb_path}")

    try:
        # Load documents
        documents = load_documents(kb_path)

        if not documents:
            print("No documents found in KB")
            return

        # Split into chunks
        chunks = split_documents(documents)

        # Create vectorstore
        vectorstore = create_vectorstore(chunks)

        # Save to disk
        store_manager = get_vector_store_manager()
        store_manager.save_vectorstore(vectorstore)

        print("Knowledge base ingestion completed successfully")

    except Exception as e:
        print(f"Knowledge base ingestion failed, error: {str(e)}")
        raise
