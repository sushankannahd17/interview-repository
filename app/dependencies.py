from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.ingestion_service import IngestionService
from app.services.interview_service import InterviewService
from app.services.progress_service import ProgressService
from app.services.question_service import QuestionService
from app.services.study_plan_service import StudyPlanService


async def get_ingestion_service(
    db: AsyncSession = Depends(get_db),
) -> IngestionService:
    return IngestionService(db)


async def get_interview_service(
    db: AsyncSession = Depends(get_db),
) -> InterviewService:
    return InterviewService(db)


async def get_question_service(
    db: AsyncSession = Depends(get_db),
) -> QuestionService:
    return QuestionService(db)


async def get_study_plan_service(
    db: AsyncSession = Depends(get_db),
) -> StudyPlanService:
    return StudyPlanService(db)


async def get_progress_service(
    db: AsyncSession = Depends(get_db),
) -> ProgressService:
    return ProgressService(db)
