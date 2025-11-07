"""
Main conversation orchestration service.
"""

from core.i18n import get_language_data
from core.sentiment import analyze_sentiment
from llm.memory import get_memory_manager
from llm.chains import get_chain_manager
from rag.retriever import query_knowledge_base
from services.extraction import get_extraction_service
from services.summarization import get_summarization_service
from services.storage import get_storage_service
from beans.schemas.conversations.chat_request_dto import ChatRequest
from beans.schemas.conversations.chat_response_dto import ChatResponse
from beans.schemas.extraction.extracted_data_dto import ExtractedData
from services import stt_tts
import base64
import datetime


class ConversationService:
    """Orchestrates conversation flow with extraction, RAG, and memory."""

    def __init__(self):
        """Initialize conversation service."""
        self.memory_manager = get_memory_manager()
        self.chain_manager = get_chain_manager()
        self.extraction_service = get_extraction_service()
        self.summarization_service = get_summarization_service()
        self.storage_service = get_storage_service()

        # Session-level extracted data cache
        self._session_data = {}

    async def process_message(self, request: ChatRequest) -> ChatResponse:
        """
        Process user message and generate response.

        Args:
            request: Chat request with session_id and message

        Returns:
            ChatResponse with reply and extracted data
        """
        session_id = request.session_id

        print(f"Processing message, message_len: {len(request.message)}")

        # Detect language
        # old version
        # language = get_language(request.message, request.language)
        language_data = await get_language_data(request.message)

        # Analyze sentiment
        sentiment, polarity = analyze_sentiment(language_data['texto_traducido'])

        # Get or create memory
        _ = self.memory_manager.get_memory(session_id)
        turn_number = self.memory_manager.get_session_count(session_id) + 1

        # Get conversation history
        history_text = self.memory_manager.get_conversation_text(session_id)

        # Extract structured information
        current_data = self._session_data.get(session_id, ExtractedData())
        extraction_result = self.extraction_service.extract_from_message(
            message=request.message,
            history=history_text,
            language=language_data['idioma_detectado'],
            current_data=current_data
        )

        # Update cached data
        self._session_data[session_id] = extraction_result.extracted

        # Check if RAG can help
        rag_context = ""
        try:
            # TODO: Esta posicion puede ser la optima para RAG
            kb_docs = query_knowledge_base(request.message, k=3)
            if kb_docs:
                rag_context = "\n\n".join(kb_docs)
                print(f"Retrieved RAG context, docs: {len(kb_docs)}")
        except Exception as e:
            print(f"RAG query failed, error: {str(e)}")

        # Generate response
        context = history_text
        if rag_context:
            context += f"\n\nRelevant information from knowledge base:\n{rag_context}"

        # Add guidance based on missing fields
        if extraction_result.missing_fields:
            missing_str = ", ".join(extraction_result.missing_fields)
            context += f"\n\nMissing required fields: {missing_str}"

        # Adjust tone for negative sentiment
        reply = self.chain_manager.generate_response(
            message=request.message,
            context=context,
            language=language_data['idioma_detectado'],
            sentiment=sentiment
        )

        # Update memory
        self.memory_manager.add_message(session_id, request.message, reply)

        # Check if we should generate summary
        summary = None
        summary_ready = extraction_result.is_complete

        if summary_ready:
            full_conversation = self.memory_manager.get_conversation_text(session_id)
            summary = self.summarization_service.generate_summary(
                conversation_text=full_conversation,
                extracted_data=extraction_result.extracted,
                language=language_data['idioma_detectado']
            )

            # Finalize storage
            self.storage_service.finalize_session(
                session_id=session_id,
                final_extracted=extraction_result.extracted,
                summary=summary
            )

        # Store turn
        self.storage_service.add_turn(
            session_id=session_id,
            turn_number=turn_number,
            user_message=request.message,
            assistant_reply=reply,
            language=language_data['idioma_detectado'],
            sentiment=sentiment,
            sentiment_polarity_value=polarity,
            extracted_delta=extraction_result.extracted
        )

        # si el usuario nos ha pedido tambien respueta en sonido, la generamos
        audio_base64 = None
        if request.audio_response:
            # Generar respuesta de audio
            audio_work_service = stt_tts.get_stt_tts_service()
            # generamos el binario del audio
            audio_data = audio_work_service.text_to_speech(reply, language=language_data['idioma_detectado'])
            # codificamos el audio a base64 para enviarlo en el json
            audio_base64 = base64.b64encode(audio_data).decode("utf-8")

        # Build response
        response = ChatResponse(
            reply=reply,
            sound_file_base64=audio_base64,
            language=language_data['idioma_detectado'],
            sentiment=sentiment,
            extracted=extraction_result.extracted,
            missing_fields=extraction_result.missing_fields,
            summary_ready=summary_ready,
            summary=summary,
            session_id=session_id,
            turn_number=turn_number
        )

        print(f"Generated response, turn: {turn_number}, is_complete: {summary_ready}")

        return response

    def reset_session(self, session_id: str) -> None:
        """
        Reset session memory and data.

        Args:
            session_id: Session to reset
        """
        self.memory_manager.clear_memory(session_id)
        self._session_data.pop(session_id, None)


# Global service
_conversation_service = None


def get_conversation_service() -> ConversationService:
    """Get global conversation service."""
    global _conversation_service
    if _conversation_service is None:
        _conversation_service = ConversationService()
    return _conversation_service
