"""
Unit tests for validators.py module.
"""
import pytest
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from utils.validators import (
    validate_order_id,
    validate_category,
    validate_urgency,
    validate_description,
    normalize_category,
    normalize_urgency
)


class TestOrderIdValidation:
    """Tests for order ID validation."""
    
    def test_valid_order_id_6_chars(self):
        """Test valid order ID with 6 characters."""
        is_valid, error = validate_order_id("ABC123")
        assert is_valid is True
        assert error is None
    
    def test_valid_order_id_12_chars(self):
        """Test valid order ID with 12 characters."""
        is_valid, error = validate_order_id("ABC123456789")
        assert is_valid is True
        assert error is None
    
    def test_valid_order_id_mixed_case(self):
        """Test valid order ID with mixed case."""
        is_valid, error = validate_order_id("aBc123XyZ")
        assert is_valid is True
        assert error is None
    
    def test_invalid_order_id_too_short(self):
        """Test invalid order ID - too short."""
        is_valid, error = validate_order_id("ABC12")
        assert is_valid is False
        assert "6-12 alphanumeric" in error
    
    def test_invalid_order_id_too_long(self):
        """Test invalid order ID - too long."""
        is_valid, error = validate_order_id("ABC1234567890")
        assert is_valid is False
        assert "6-12 alphanumeric" in error
    
    def test_invalid_order_id_special_chars(self):
        """Test invalid order ID - contains special characters."""
        is_valid, error = validate_order_id("ABC-123456")
        assert is_valid is False
        assert "alphanumeric" in error
    
    def test_invalid_order_id_empty(self):
        """Test invalid order ID - empty string."""
        is_valid, error = validate_order_id("")
        assert is_valid is False
        assert "cannot be empty" in error
    
    def test_order_id_with_whitespace(self):
        """Test order ID with surrounding whitespace."""
        is_valid, error = validate_order_id("  ABC123456  ")
        assert is_valid is True
        assert error is None


class TestCategoryValidation:
    """Tests for category validation and normalization."""
    
    def test_valid_category_english(self):
        """Test valid category in English."""
        for category in ["shipping", "billing", "technical", "other"]:
            is_valid, error = validate_category(category)
            assert is_valid is True
            assert error is None
    
    def test_valid_category_spanish(self):
        """Test valid category translated from Spanish."""
        spanish_categories = {
            "envío": "shipping",
            "envio": "shipping",
            "facturación": "billing",
            "factura": "billing",
            "técnico": "technical",
            "otro": "other"
        }
        
        for spanish, english in spanish_categories.items():
            normalized = normalize_category(spanish)
            assert normalized == english
    
    def test_invalid_category(self):
        """Test invalid category."""
        is_valid, error = validate_category("invalid_category")
        assert is_valid is False
        assert "must be one of" in error
    
    def test_normalize_category_case_insensitive(self):
        """Test category normalization is case insensitive."""
        assert normalize_category("SHIPPING") == "shipping"
        assert normalize_category("Billing") == "billing"
        assert normalize_category("TeChNiCaL") == "technical"
    
    def test_normalize_category_with_whitespace(self):
        """Test category normalization handles whitespace."""
        assert normalize_category("  shipping  ") == "shipping"
        assert normalize_category("  envío  ") == "shipping"
    
    def test_normalize_category_empty(self):
        """Test normalizing empty category."""
        assert normalize_category("") is None
        assert normalize_category(None) is None


class TestUrgencyValidation:
    """Tests for urgency validation and normalization."""
    
    def test_valid_urgency_english(self):
        """Test valid urgency in English."""
        for urgency in ["low", "medium", "high"]:
            is_valid, error = validate_urgency(urgency)
            assert is_valid is True
            assert error is None
    
    def test_valid_urgency_spanish(self):
        """Test valid urgency translated from Spanish."""
        spanish_urgencies = {
            "baja": "low",
            "bajo": "low",
            "media": "medium",
            "medio": "medium",
            "alta": "high",
            "alto": "high",
            "urgente": "high"
        }
        
        for spanish, english in spanish_urgencies.items():
            normalized = normalize_urgency(spanish)
            assert normalized == english
    
    def test_invalid_urgency(self):
        """Test invalid urgency."""
        is_valid, error = validate_urgency("invalid_urgency")
        assert is_valid is False
        assert "must be one of" in error
    
    def test_normalize_urgency_case_insensitive(self):
        """Test urgency normalization is case insensitive."""
        assert normalize_urgency("LOW") == "low"
        assert normalize_urgency("Medium") == "medium"
        assert normalize_urgency("HIGH") == "high"
    
    def test_normalize_urgency_with_whitespace(self):
        """Test urgency normalization handles whitespace."""
        assert normalize_urgency("  high  ") == "high"
        assert normalize_urgency("  urgente  ") == "high"
    
    def test_normalize_urgency_empty(self):
        """Test normalizing empty urgency."""
        assert normalize_urgency("") is None
        assert normalize_urgency(None) is None


class TestDescriptionValidation:
    """Tests for description validation."""
    
    def test_valid_description(self):
        """Test valid description."""
        is_valid, error = validate_description("Mi pedido no ha llegado después de 2 semanas")
        assert is_valid is True
        assert error is None
    
    def test_valid_description_exactly_min_length(self):
        """Test description with exactly minimum length."""
        is_valid, error = validate_description("1234567890")  # 10 chars
        assert is_valid is True
        assert error is None
    
    def test_invalid_description_too_short(self):
        """Test invalid description - too short."""
        is_valid, error = validate_description("Short", min_length=10)
        assert is_valid is False
        assert "at least 10 characters" in error
    
    def test_invalid_description_empty(self):
        """Test invalid description - empty."""
        is_valid, error = validate_description("")
        assert is_valid is False
        assert "cannot be empty" in error
    
    def test_description_with_whitespace(self):
        """Test description with surrounding whitespace."""
        is_valid, error = validate_description("  Valid description here  ")
        assert is_valid is True
        assert error is None
    
    def test_description_custom_min_length(self):
        """Test description with custom minimum length."""
        is_valid, error = validate_description("Short", min_length=5)
        assert is_valid is True
        assert error is None
        
        is_valid, error = validate_description("Short", min_length=20)
        assert is_valid is False
        assert "at least 20 characters" in error
