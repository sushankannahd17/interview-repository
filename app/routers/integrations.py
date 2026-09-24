from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse

from app.dependencies import get_ingestion_service
from app.middleware.auth import verify_team_b_key
from app.schemas.interview import InterviewResponse
from app.schemas.team_b import TeamBInterviewPayload
from app.services.ingestion_service import IngestionService

router = APIRouter(prefix="/integrations/team-b", tags=["Team B Integration"])


@router.post(
    "/interviews",
    response_model=InterviewResponse,
    responses={
        200: {"description": "Duplicate — existing record returned"},
        201: {"description": "Interview created successfully"},
    },
)
async def ingest_interview(
    payload: TeamBInterviewPayload,
    _: None = Depends(verify_team_b_key),
    service: IngestionService = Depends(get_ingestion_service),
) -> Response:
    result, created = await service.ingest_interview(payload)
    status_code = 201 if created else 200
    return JSONResponse(
        content=result.model_dump(mode="json"),
        status_code=status_code,
    )
