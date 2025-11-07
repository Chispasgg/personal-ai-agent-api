"""
LLM and embeddings model wrappers.
"""
from typing import Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_anthropic import ChatAnthropic
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.embeddings.base import Embeddings
from config.settings import settings
from langchain_core.language_models.base import BaseLanguageModel
from langchain_community.llms.ollama import Ollama


def get_llm(temperature: Optional[float]=None, max_tokens: Optional[int]=None) -> BaseLanguageModel:
    """
    Get LLM instance based on configuration.

    Args:
        temperature: Override default temperature
        max_tokens: Override default max tokens

    Returns:
        LangChain LLM instance
    """
    temp = temperature if temperature is not None else settings.llm_temperature
    tokens = max_tokens if max_tokens is not None else settings.llm_max_tokens

    try:
        if settings.llm_provider == "openai":
            print(f"Initializing OpenAI LLM, model: {settings.llm_model}")
            return ChatOpenAI(
                model=settings.llm_model,
                temperature=temp,
                max_tokens=tokens,
                openai_api_key=settings.openai_api_key
            )

        elif settings.llm_provider == "anthropic":
            print(f"Initializing Anthropic LLM, model: {settings.llm_model}")
            return ChatAnthropic(
                model=settings.llm_model,
                temperature=temp,
                max_tokens=tokens,
                anthropic_api_key=settings.anthropic_api_key
            )

        elif settings.llm_provider == "local":
            print(f"Initializing local LLM, endpoint: {settings.local_llm_endpoint}")
            # For local models (e.g., Ollama)
            return Ollama(
                base_url=settings.local_llm_endpoint,
                model=settings.llm_model,
                temperature=temp
            )

        else:
            raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")

    except Exception as e:
        print(f"Failed to initialize LLM, error: {str(e)}")
        raise


def get_embeddings() -> Embeddings:
    """
    Get embeddings model based on configuration.

    Returns:
        LangChain embeddings instance
    """
    try:
        if settings.embeddings_provider == "openai":
            print(f"Initializing OpenAI embeddings, model: {settings.embeddings_model}")
            return OpenAIEmbeddings(
                model=settings.embeddings_model,
                openai_api_key=settings.openai_api_key
            )

        elif settings.embeddings_provider == "huggingface":
            print(f"Initializing HuggingFace embeddings, model: {settings.embeddings_model}")
            return HuggingFaceEmbeddings(
                model_name=settings.embeddings_model,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )

        else:
            raise ValueError(f"Unsupported embeddings provider: {settings.embeddings_provider}")

    except Exception as e:
        print(f"Failed to initialize embeddings, error: {str(e)}")
        raise
