"""
Conversation summarization service.
"""
from llm.chains import get_chain_manager
from beans.schemas.extraction.extracted_data_dto import ExtractedData


class SummarizationService:
    """Service for generating conversation summaries."""

    def __init__(self):
        """Initialize summarization service."""
        self.chain_manager = get_chain_manager()

    def generate_summary(
        self,
        conversation_text: str,
        extracted_data: ExtractedData,
        language: str="es"
    ) -> str:
        """
        Generate summary of conversation.

        Args:
            conversation_text: Full conversation as text
            extracted_data: Extracted structured data
            language: Language code

        Returns:
            Summary text
        """
        try:
            summary = self.chain_manager.generate_summary(
                conversation=conversation_text,
                extracted_data=extracted_data.model_dump(),
                language=language
            )

            print(f"Generated summary, length: {len(summary)}")
            return summary

        except Exception as e:
            print(f"Summarization failed, error: {str(e)}")
            return "Error generating summary"


# Global service
_summarization_service = None


def get_summarization_service() -> SummarizationService:
    """Get global summarization service."""
    global _summarization_service
    if _summarization_service is None:
        _summarization_service = SummarizationService()
    return _summarization_service
