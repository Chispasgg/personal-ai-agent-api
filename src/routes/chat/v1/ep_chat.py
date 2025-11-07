"""
Chat endpoints.
"""
from fastapi import APIRouter, HTTPException, status
from services.conversation import get_conversation_service
from beans.schemas.conversations.chat_request_dto import ChatRequest
from beans.schemas.conversations.chat_response_dto import ChatResponse

endpoint_type = 'api/v1/chat'
route_prefix = f"/{endpoint_type}"

router = APIRouter(
    prefix=route_prefix,
    tags=["Chat Zone"],
    responses={404: {"description": "Not found"}},
)


@router.post("/",
             summary="",
             description="",
             response_model_exclude_none=True)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Process chat message and return response.

    Args:
        request: ChatRequest with session_id and message

    Returns:
        ChatResponse with reply and extracted data
    """
    request.language = None  # Force language detection
    try:
        conversation_service = get_conversation_service()
        response = await conversation_service.process_message(request)
        return response

    except ValueError as e:
        print(f"Validation error in chat {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        print(f"Error processing chat {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message"
        )
