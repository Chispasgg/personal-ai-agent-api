"""
Validation functions for structured data fields.
"""
import re
from typing import Optional, Literal

# Type aliases
Category = Literal["shipping", "billing", "technical", "other"]
Urgency = Literal["low", "medium", "high"]

# Validation patterns
ORDER_ID_PATTERN = re.compile(r'^[A-Z0-9]{6,12}$', re.IGNORECASE)

# Valid enum values
VALID_CATEGORIES = {"shipping", "billing", "technical", "other"}
VALID_URGENCIES = {"low", "medium", "high"}

# Category translations
CATEGORY_TRANSLATIONS = {
    "envío": "shipping",
    "envio": "shipping",
    "envios": "shipping",
    "envíos": "shipping",
    "facturación": "billing",
    "facturacion": "billing",
    "factura": "billing",
    "pago": "billing",
    "pagos": "billing",
    "técnico": "technical",
    "tecnico": "technical",
    "técnica": "technical",
    "tecnica": "technical",
    "otro": "other",
    "otra": "other",
    "otros": "other",
}

# Urgency translations
URGENCY_TRANSLATIONS = {
    "baja": "low",
    "bajo": "low",
    "media": "medium",
    "medio": "medium",
    "alta": "high",
    "alto": "high",
    "urgente": "high",
}


def validate_order_id(order_id: str) -> tuple[bool, Optional[str]]:
    """
    Validate order ID format.

    Args:
        order_id: Order ID to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not order_id:
        return False, "Order ID cannot be empty"

    order_id = order_id.strip()

    if not ORDER_ID_PATTERN.match(order_id):
        return False, "Order ID must be 6-12 alphanumeric characters"

    return True, None


def normalize_category(category: str) -> Optional[str]:
    """
    Normalize and validate category value.
    Translates Spanish terms to English.

    Args:
        category: Category to normalize

    Returns:
        Normalized category or None if invalid
    """
    if not category:
        return None

    category_lower = category.strip().lower()

    # Check if already valid English value
    if category_lower in VALID_CATEGORIES:
        return category_lower

    # Try translation
    if category_lower in CATEGORY_TRANSLATIONS:
        return CATEGORY_TRANSLATIONS[category_lower]

    print(f"Invalid category value, category: {category}")
    return None


def validate_category(category: str) -> tuple[bool, Optional[str]]:
    """
    Validate category value.

    Args:
        category: Category to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    normalized = normalize_category(category)

    if normalized is None:
        return False, f"Category must be one of: {', '.join(VALID_CATEGORIES)}"

    return True, None


def normalize_urgency(urgency: str) -> Optional[str]:
    """
    Normalize and validate urgency value.
    Translates Spanish terms to English.

    Args:
        urgency: Urgency to normalize

    Returns:
        Normalized urgency or None if invalid
    """
    if not urgency:
        return None

    urgency_lower = urgency.strip().lower()

    # Check if already valid English value
    if urgency_lower in VALID_URGENCIES:
        return urgency_lower

    # Try translation
    if urgency_lower in URGENCY_TRANSLATIONS:
        return URGENCY_TRANSLATIONS[urgency_lower]

    print(f"Invalid urgency value, urgency: {urgency}")
    return None


def validate_urgency(urgency: str) -> tuple[bool, Optional[str]]:
    """
    Validate urgency value.

    Args:
        urgency: Urgency to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    normalized = normalize_urgency(urgency)

    if normalized is None:
        return False, f"Urgency must be one of: {', '.join(VALID_URGENCIES)}"

    return True, None


def validate_description(description: str, min_length: int=10) -> tuple[bool, Optional[str]]:
    """
    Validate description field.

    Args:
        description: Description to validate
        min_length: Minimum required length

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not description:
        return False, "Description cannot be empty"

    description = description.strip()

    if len(description) < min_length:
        return False, f"Description must be at least {min_length} characters"

    return True, None
