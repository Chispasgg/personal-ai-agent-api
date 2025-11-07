'''
Created on 6 nov 2025

@author: chispas
'''
from pydantic import BaseModel, Field
from beans.schemas.extraction import extracted_data_dto


class ExtractionResult(BaseModel):
    """Result of extraction operation."""

    extracted: extracted_data_dto.ExtractedData = Field(..., description="Extracted data")
    missing_fields: list[str] = Field(default_factory=list, description="Missing required fields")
    validation_errors: dict[str, str] = Field(default_factory=dict, description="Validation errors by field")
    is_complete: bool = Field(False, description="Whether all fields are present")
