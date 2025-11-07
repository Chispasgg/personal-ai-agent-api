'''
Created on 6 nov 2025

@author: chispas
'''
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from beans.schemas import schemas_litrerals
from utils.validators import validate_order_id, validate_description, normalize_category, normalize_urgency


class ExtractedData(BaseModel):
    """Extracted structured data from conversation."""

    order_id: Optional[str] = Field(None, description="Order ID (6-12 alphanumeric characters)")
    category: Optional[schemas_litrerals.Category] = Field(None, description="Support category")
    description: Optional[str] = Field(None, description="Problem description")
    urgency: Optional[schemas_litrerals.Urgency] = Field(None, description="Urgency level")

    @field_validator("order_id")
    @classmethod
    def validate_order_id_field(cls, v: Optional[str]) -> Optional[str]:
        """Validate order_id format."""
        if v is None:
            return v

        is_valid, error = validate_order_id(v)
        if not is_valid:
            raise ValueError(error or "Invalid order ID")

        return v.strip().upper()

    @field_validator("category", mode="before")
    @classmethod
    def normalize_category_field(cls, v: Optional[str]) -> Optional[str]:
        """Normalize category value."""
        if v is None:
            return v

        normalized = normalize_category(v)
        if normalized is None:
            raise ValueError(f"Invalid category: {v}")

        return normalized

    @field_validator("urgency", mode="before")
    @classmethod
    def normalize_urgency_field(cls, v: Optional[str]) -> Optional[str]:
        """Normalize urgency value."""
        if v is None:
            return v

        normalized = normalize_urgency(v)
        if normalized is None:
            raise ValueError(f"Invalid urgency: {v}")

        return normalized

    @field_validator("description")
    @classmethod
    def validate_description_field(cls, v: Optional[str]) -> Optional[str]:
        """Validate description."""
        if v is None:
            return v

        is_valid, error = validate_description(v, min_length=10)
        if not is_valid:
            raise ValueError(error or "Invalid description")

        return v.strip()

    def get_missing_fields(self) -> list[str]:
        """
        Get list of missing required fields.

        Returns:
            List of missing field names
        """
        missing = []
        if self.order_id is None:
            missing.append("order_id")
        if self.category is None:
            missing.append("category")
        if self.description is None:
            missing.append("description")
        if self.urgency is None:
            missing.append("urgency")

        return missing

    def is_complete(self) -> bool:
        """
        Check if all required fields are present.

        Returns:
            True if all fields are filled
        """
        return len(self.get_missing_fields()) == 0

    def merge(self, other: "ExtractedData") -> "ExtractedData":
        """
        Merge with another ExtractedData, keeping non-None values.

        Args:
            other: Other ExtractedData instance

        Returns:
            New merged ExtractedData
        """
        return ExtractedData(
            order_id=other.order_id or self.order_id,
            category=other.category or self.category,
            description=other.description or self.description,
            urgency=other.urgency or self.urgency
        )
