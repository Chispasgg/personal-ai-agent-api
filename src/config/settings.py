"""
Configuration management using Pydantic Settings.
Loads environment variables from .env file.
"""
from typing import List, Literal
from pathlib import Path
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation."""

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_env: Literal["dev", "prod", "test"] = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"

    # Security
    api_key_admin: str = Field(default="changeme")

    # LLM Configuration
    llm_provider: Literal["openai", "anthropic", "local"] = "openai"
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 1000

    # API Keys
    openai_api_key: str = Field(default="")
    anthropic_api_key: str = Field(default="")
    local_llm_endpoint: str = "http://localhost:11434"

    # Knowledge Base
    kb_path: str = Field(default="../kb")

    # Embeddings
    embeddings_provider: Literal["openai", "huggingface"] = "openai"
    embeddings_model: str = "text-embedding-3-large"

    # Vector Store
    vectorstore_path: str = "./data/vectorstore"
    vectorstore_index_name: str = "faiss_index"

    # RAG Configuration
    rag_top_k: int = 5
    rag_score_threshold: float = 0.7
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # Conversation
    max_conversation_turns: int = 50
    conversation_storage_path: str = "./data/conversations"

    # Rate Limiting
    rate_limit_max_requests: int = 100
    rate_limit_window_seconds: int = 3600

    # Input Validation
    max_message_length: int = 2000

    # Sentiment Analysis
    sentiment_threshold_negative: float = -0.3
    sentiment_threshold_positive: float = 0.3

    # TTS/STT
    tts_enabled: bool = False
    tts_provider: str = "gtts"
    stt_enabled: bool = False
    stt_provider: str = "none"

    # Languages
    default_language: str = "es"
    supported_languages: str = "es,en"

    @field_validator("vectorstore_path", "conversation_storage_path")
    @classmethod
    def create_directories(cls, v: str) -> str:
        """Ensure directories exist."""
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        return v

    @property
    def supported_languages_list(self) -> List[str]:
        """Get list of supported languages."""
        return [lang.strip() for lang in self.supported_languages.split(",")]

    def validate_api_keys(self) -> None:
        """Validate that required API keys are set based on provider."""
        if self.llm_provider == "openai" and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI provider")
        if self.llm_provider == "anthropic" and not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is required when using Anthropic provider")
        if self.embeddings_provider == "openai" and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required when using OpenAI embeddings")


# Global settings instance
settings = Settings()
