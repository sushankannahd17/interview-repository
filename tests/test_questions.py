import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.interview import InterviewExperience
from app.models.question import Question
from tests.conftest import COMPANY_UUID, STUDENT_UUID

QUESTIONS_URL = "/api/v1/questions"


async def _seed_questions(db_session: AsyncSession) -> list[Question]:
    interview = InterviewExperience(
        student_id=STUDENT_UUID,
        company_id=COMPANY_UUID,
        role="Backend Developer",
        interview_date="2026-09-15",
        difficulty="MEDIUM",
        experience_text="Test",
        source_system="TEAM_B",
        source_record_id="q-test-int",
        status="ACTIVE",
        questions=[
            Question(
                question_text="Explain B-trees",
                category="DBMS",
                difficulty="HARD",
                source_system="TEAM_B",
                source_record_id="qt-001",
            ),
            Question(
                question_text="Reverse a linked list",
                category="DSA",
                difficulty="EASY",
                source_system="TEAM_B",
                source_record_id="qt-002",
            ),
            Question(
                question_text="Explain TCP handshake",
                category="NETWORKING",
                difficulty="MEDIUM",
                source_system="TEAM_B",
                source_record_id="qt-003",
            ),
        ],
    )
    db_session.add(interview)
    await db_session.flush()
    return interview.questions


@pytest.mark.asyncio
async def test_list_questions(
    client: AsyncClient, db_session: AsyncSession, seed_all, student_auth_headers
):
    await _seed_questions(db_session)

    response = await client.get(QUESTIONS_URL, headers=student_auth_headers)
    assert response.status_code == 200
    assert response.json()["total_elements"] == 3


@pytest.mark.asyncio
async def test_filter_questions_by_category(
    client: AsyncClient, db_session: AsyncSession, seed_all, student_auth_headers
):
    await _seed_questions(db_session)

    response = await client.get(f"{QUESTIONS_URL}?category=DSA", headers=student_auth_headers)
    assert response.status_code == 200

    data = response.json()
    for item in data["items"]:
        assert item["category"] == "DSA"


@pytest.mark.asyncio
async def test_filter_questions_by_difficulty(
    client: AsyncClient, db_session: AsyncSession, seed_all, student_auth_headers
):
    await _seed_questions(db_session)

    response = await client.get(f"{QUESTIONS_URL}?difficulty=HARD", headers=student_auth_headers)
    assert response.status_code == 200

    data = response.json()
    for item in data["items"]:
        assert item["difficulty"] == "HARD"


@pytest.mark.asyncio
async def test_get_question_by_id(
    client: AsyncClient, db_session: AsyncSession, seed_all, student_auth_headers
):
    questions = await _seed_questions(db_session)

    response = await client.get(f"{QUESTIONS_URL}/{questions[0].id}", headers=student_auth_headers)
    assert response.status_code == 200
    assert response.json()["question_text"] == "Explain B-trees"
