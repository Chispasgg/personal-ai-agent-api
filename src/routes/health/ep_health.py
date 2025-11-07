"""
Chat endpoints.
"""
from fastapi import APIRouter

from __init__ import __pgg_version__
from beans.schemas.status.health_response_dto import HealthResponse

endpoint_type = 'api/health'
route_prefix = f"/{endpoint_type}"

router = APIRouter(
    prefix=route_prefix,
    tags=["Health"],
    responses={404: {"description": "Not found"}},
)


@router.get("/",
            summary="",
             description="",
             response_model_exclude_none=True)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="ok", version=__pgg_version__)
