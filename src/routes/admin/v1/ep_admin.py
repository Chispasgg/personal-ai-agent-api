"""
Admin endpoints for ingestion, stats, and management.
"""
from fastapi import APIRouter, HTTPException, Header, status

from rag.ingest import ingest_knowledge_base
from services.storage import get_storage_service
from beans.api.admin.ingest_response_dto import IngestResponse
from beans.api.admin.ingest_request_dto import IngestRequest
from routes.admin.utils import admin_utils

endpoint_type = 'api/v1/admin'
route_prefix = f"/{endpoint_type}"

router = APIRouter(
    prefix=route_prefix,
    tags=["Admin Zone"],
    responses={404: {"description": "Not found"}},
)


@router.post("/ingest",
             summary="",
             description="",
             response_model_exclude_none=True)
async def trigger_ingest(
    request: IngestRequest,
    x_api_key: str=Header(None)
) -> IngestResponse:
    """
    Trigger knowledge base ingestion.

    Requires admin API key in X-API-Key header.
    """
    admin_utils.verify_admin_key(x_api_key)

    try:
        print(f"Admin triggered ingestion, kb_path: {request.kb_path}")
        ingest_knowledge_base(request.kb_path)

        return IngestResponse(
            status="success",
            message="Knowledge base ingested successfully"
        )

    except Exception as e:
        print(f"Ingestion failed, error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion failed: {str(e)}"
        )


@router.get("/session/{session_id}",
            summary="",
             description="",
             response_model_exclude_none=True)
async def get_session(
    session_id: str,
    x_api_key: str=Header(None)
    ):
    """
    Retrieve session data.

    Requires admin API key.
    """
    admin_utils.verify_admin_key(x_api_key)

    storage_service = get_storage_service()
    session = storage_service.load_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    return session
