import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.exceptions import EntityNotFoundError
from app.models.alumni import PlacedAlumni
from app.models.company import Company
from app.models.interview import InterviewExperience
from app.models.question import Question
from app.models.student import Student
from app.repositories.interview_repository import InterviewRepository
from app.schemas.interview import InterviewResponse
from app.schemas.team_b import TeamBInterviewPayload

logger = structlog.get_logger()

SOURCE_SYSTEM = "TEAM_B"


class IngestionService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.interview_repo = InterviewRepository(session)

    async def ingest_interview(
        self, payload: TeamBInterviewPayload
    ) -> tuple[InterviewResponse, bool]:
        existing = await self.interview_repo.find_by_source(SOURCE_SYSTEM, payload.source_id)
        if existing:
            logger.info(
                "duplicate_ingestion_skipped",
                source_id=payload.source_id,
                existing_id=str(existing.id),
            )
            existing_with_q = await self.interview_repo.get_with_questions(existing.id)
            return InterviewResponse.model_validate(existing_with_q), False

        student = await self.session.get(Student, payload.student_id)
        if not student:
            raise EntityNotFoundError("Student", str(payload.student_id))

        company = await self.session.get(Company, payload.company_id)
        if not company:
            raise EntityNotFoundError("Company", str(payload.company_id))

        if payload.alumni_id:
            alumni = await self.session.get(PlacedAlumni, payload.alumni_id)
            if not alumni:
                raise EntityNotFoundError("Alumni", str(payload.alumni_id))

        interview = InterviewExperience(
            student_id=payload.student_id,
            company_id=payload.company_id,
            alumni_id=payload.alumni_id,
            role=payload.role,
            interview_date=payload.interview_date,
            difficulty=payload.difficulty.value,
            experience_text=payload.experience_text,
            tips=payload.tips,
            source_system=SOURCE_SYSTEM,
            source_record_id=payload.source_id,
            status="ACTIVE",
            questions=[
                Question(
                    question_text=q.question_text,
                    category=q.category.value,
                    difficulty=q.difficulty.value,
                    expected_answer=q.expected_answer,
                    source_system=SOURCE_SYSTEM,
                    source_record_id=q.source_id,
                )
                for q in payload.questions
            ],
        )

        created = await self.interview_repo.create_with_questions(interview)
        await self.session.commit()

        logger.info(
            "interview_ingested",
            source_id=payload.source_id,
            interview_id=str(created.id),
            question_count=len(payload.questions),
        )

        return InterviewResponse.model_validate(created), True
