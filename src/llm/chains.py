"""
LangChain chains for RAG, extraction, and summarization.
"""
from typing import Dict, Any, Optional
import json

from langchain_classic.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain_core.prompts.prompt import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from llm import models, prompts


class ChainManager:
    """Manages different LangChain chains for various tasks."""

    def __init__(self):
        """Initialize chain manager."""
        self.llm = models.get_llm()

    def create_rag_chain(self, retriever, language: str="es"):
        """
        Create RAG chain with retriever.

        Args:
            retriever: LangChain retriever
            language: Language code

        Returns:
            ConversationalRetrievalChain instance
        """
        print(f"Creating RAG chain, language: {language}")

        # Create conversational retrieval chain
        chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            return_source_documents=True,
            verbose=False
        )

        return chain

    def extract_structured_info(
        self,
        message: str,
        history: str
    ) -> Dict[str, Any]:
        """
        Extract structured information from message.

        Args:
            message: User message
            history: Conversation history
            language: Language code

        Returns:
            Dictionary with extracted fields
        """

        prompt_template = prompts.get_extraction_prompt_template()
        # Use modern RunnableSequence with | operator
        chain = prompt_template | self.llm | StrOutputParser()

        try:
            result = chain.invoke({'message': message, 'history': history})

            # Parse JSON response
            extracted = json.loads(result.replace('```json', '').replace('```', '').strip())

            print(f"Successfully extracted structured info, fields: {list(extracted.keys())}")
            return extracted

        except json.JSONDecodeError as e:
            print(f"Failed to parse extraction JSON, error: {str(e)}, response: {result}")
            return {}
        except Exception as e:
            print(f"Extraction failed, error: {str(e)}")
            return {}

    def generate_summary(
        self,
        conversation: str,
        extracted_data: Dict[str, Any],
        language: str="es"
    ) -> str:
        """
        Generate conversation summary.

        Args:
            conversation: Full conversation text
            extracted_data: Extracted structured data
            language: Language code

        Returns:
            Summary text
        """
        print(f"Generating conversation summary, language: {language}")

        summary_prompt = prompts.get_summary_prompt(language)

        prompt_template = PromptTemplate(
            template=summary_prompt,
            input_variables=["conversation", "order_id", "category", "description", "urgency"]
        )

        # Use modern RunnableSequence with | operator
        chain = prompt_template | self.llm | StrOutputParser()

        try:
            summary = chain.invoke({
                "conversation": conversation,
                "order_id": extracted_data.get("order_id", "N/A"),
                "category": extracted_data.get("category", "N/A"),
                "description": extracted_data.get("description", "N/A"),
                "urgency": extracted_data.get("urgency", "N/A")
            })

            print("Successfully generated summary")
            return summary.strip()

        except Exception as e:
            print(f"Summary generation failed, error: {str(e)}")
            return "Error generating summary"

    def generate_response(
        self,
        message: str,
        context: str,
        language: str="es",
        sentiment: str="neutral"
    ) -> str:
        """
        Generate contextual response without RAG.

        Args:
            message: User message
            context: Conversation context
            language: Language code
            sentiment: Detected sentiment

        Returns:
            Generated response
        """
        system_prompt = prompts.get_system_prompt(language)

        # Adjust tone based on sentiment
        if sentiment == "negative":
            system_prompt += "\n\nIMPORTANT: The user seems frustrated. Be extra empathetic and helpful."

        prompt_template = PromptTemplate(
            template=f"{system_prompt}\n\nContext:\n{{context}}\n\nUser: {{message}}\n\nAssistant:",
            input_variables=["context", "message"]
        )

        # Use modern RunnableSequence with | operator
        chain = prompt_template | self.llm | StrOutputParser()

        try:
            response = chain.invoke({"context": context, "message": message})
            return response.strip()
        except Exception as e:
            print(f"Response generation failed, error: {str(e)}")
            return "I apologize, but I'm having trouble processing your request. Please try again."


# Global chain manager
_chain_manager: Optional[ChainManager] = None


def get_chain_manager() -> ChainManager:
    """
    Get global chain manager instance.

    Returns:
        ChainManager instance
    """
    global _chain_manager
    if _chain_manager is None:
        _chain_manager = ChainManager()
    return _chain_manager
