"""
Prompt templates for different tasks and languages.
"""

from langchain_core.prompts.prompt import PromptTemplate
import langcodes

# System prompts by language
SYSTEM_PROMPTS:str = """You are a professional and empathetic customer support assistant.

Your goal is to help users resolve their inquiries by collecting the following information:
- Order ID (order_id): alphanumeric format, 6-12 characters
- Category (category): shipping, billing, technical, or other
- Description (description): detailed description of the problem
- Urgency (urgency): low, medium, or high

Behavior guidelines:
1. Be kind, professional, and empathetic
2. Ask ONE question at a time to avoid overwhelming the user
3. Validate each field before proceeding
4. If you detect frustration, show more empathy and offer immediate help
5. Use knowledge base information when relevant
6. Maintain context throughout the conversation
7. When you have all validated fields, create a summary
8. Answer in [{USER_LANGUAGE}] language.

DO NOT make up information. If you don't know something, state it clearly."""

# Summary prompts
SUMMARY_PROMPTS:str = """Create a concise summary of the following support conversation in [{USER_LANGUAGE}].

Conversation:
{conversation}

Collected information:
- Order ID: {order_id}
- Category: {category}
- Description: {description}
- Urgency: {urgency}

Create a summary that includes:
1. Brief problem summary
2. Key information collected
3. Suggested next steps
4. Customer satisfaction level (estimated from tone)

Summary:"""

EXTRACTION_PROMPT_TEMPLATE = """Analyze the following message and extract structured information.

Message: {message}

History: {history}

Extract ONLY explicit information for: order_id, category, description, urgency.
Respond with valid JSON."""


def __get_user_language(language_code: str) -> str:
    """
    Obtiene el lenguaje del usuario basado en el código proporcionado.

    Args:
        language_code (str): Código del lenguaje (e.g., 'en', 'es').

    Returns:
        str: Nombre completo del lenguaje.
    """
    language_name = "Spanish"  # Valor predeterminado
    try:
        # Intenta obtener el nombre del lenguaje usando langcodes
        language_name = langcodes.Language.get(language_code).display_name('en')
    except Exception:
        pass

    return language_name


def get_system_prompt(user_language:str="es") -> str:
    """Get system prompt."""
    return SYSTEM_PROMPTS.replace("[{USER_LANGUAGE}]", __get_user_language(user_language))


def get_extraction_prompt_template() -> PromptTemplate:

    return PromptTemplate(
        template=EXTRACTION_PROMPT_TEMPLATE,
        input_variables=["message", "history"]
    )


def get_summary_prompt(user_language:str="es") -> str:
    """Get summary prompt for language."""
    return SUMMARY_PROMPTS.replace("[{USER_LANGUAGE}]", __get_user_language(user_language))
