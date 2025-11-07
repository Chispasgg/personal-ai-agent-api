"""
Information extraction service.
"""

from llm.chains import get_chain_manager
from beans.schemas.extraction.extracted_data_dto import ExtractedData
from beans.schemas.extraction.extraction_result_dto import ExtractionResult


class ExtractionService:
    """Service for extracting structured information from conversations."""

    def __init__(self):
        """Initialize extraction service."""
        self.chain_manager = get_chain_manager()

    def extract_from_message(
        self,
        message: str,
        history: str,
        language: str="es",
        current_data: ExtractedData | None=None
    ) -> ExtractionResult:
        """
        Extract structured information from message.

        Args:
            message: User message
            history: Conversation history
            language: Language code
            current_data: Previously extracted data

        Returns:
            ExtractionResult with extracted and validation info
        """
        try:
            # Extract using LLM
            extracted_dict = self.chain_manager.extract_structured_info(
                message=message,
                history=history
            )

            # Parse into ExtractedData
            try:
                new_data = ExtractedData(**extracted_dict)
            except Exception as e:
                print(f"Failed to parse extracted data, error: {str(e)}")
                new_data = ExtractedData()

            # Merge with current data
            if current_data:
                merged_data = current_data.merge(new_data)
            else:
                merged_data = new_data

            # Build result
            result = ExtractionResult(
                extracted=merged_data,
                missing_fields=merged_data.get_missing_fields(),
                is_complete=merged_data.is_complete()
            )

            print(f"Extraction completed, is_complete: {result.is_complete}, missing: {len(result.missing_fields)}")

            return result

        except Exception as e:
            print(f"Extraction failed, error: {str(e)}")
            # Return current data or empty
            return ExtractionResult(
                extracted=current_data or ExtractedData(),
                missing_fields=(current_data or ExtractedData()).get_missing_fields(),
                is_complete=False
            )


# Global service
_extraction_service = None


def get_extraction_service() -> ExtractionService:
    """Get global extraction service."""
    global _extraction_service
    if _extraction_service is None:
        _extraction_service = ExtractionService()
    return _extraction_service
