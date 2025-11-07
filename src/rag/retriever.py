"""
RAG retriever for querying vector store.
"""

from langchain_classic.retrievers.document_compressors.chain_extract import LLMChainExtractor
from langchain_classic.retrievers.contextual_compression import ContextualCompressionRetriever
from config.settings import settings
from llm.models import get_embeddings, get_llm
from rag.store import get_vector_store_manager


def get_retriever(use_compression: bool=False):
    """
    Get retriever for RAG queries.

    Args:
        use_compression: Whether to use contextual compression

    Returns:
        LangChain retriever
    """
    print("Initializing retriever")

    # Load vectorstore
    store_manager = get_vector_store_manager()
    embeddings = get_embeddings()
    vectorstore = store_manager.load_vectorstore(embeddings)

    if vectorstore is None:
        print(f"Vectorstore not found, RAG will not be available")
        return None

    # Create base retriever
    base_retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": settings.rag_top_k}
    )

    if use_compression:
        # Add contextual compression
        print("Using contextual compression retriever")
        llm = get_llm()
        compressor = LLMChainExtractor.from_llm(llm)
        retriever = ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=base_retriever
        )
        return retriever

    return base_retriever


def query_knowledge_base(question: str, k: int=3) -> list[str]:
    """
    Query knowledge base and return relevant documents.

    Args:
        question: Query question
        k: Number of documents to return

    Returns:
        List of relevant document texts
    """
    store_manager = get_vector_store_manager()
    embeddings = get_embeddings()
    vectorstore = store_manager.load_vectorstore(embeddings)

    if vectorstore is None:
        print(f"Vectorstore not available")
        return []

    try:
        docs = vectorstore.similarity_search(question, k=k)
        return [doc.page_content for doc in docs]
    except Exception as e:
        print(f"Failed to query knowledge base, error: {str(e)}")
        return []
