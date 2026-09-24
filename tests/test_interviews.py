import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.interview import InterviewExperience
from app.models.question import Question
from tests.conftest import COMPANY_UUID, STUDENT_UUID

INTERVIEWS_URL = "/api/v1/interviews"


async def _seed_interview(
    db_session: AsyncSession,
    source_id: str = "src-001",
    difficulty: str = "HARD",
) -> InterviewExperience:
    interview = InterviewExperience(
        student_id=STUDENT_UUID,
        company_id=COMPANY_UUID,
        role="Software Engineer",
        interview_date="2026-09-20",
        difficulty=difficulty,
        experience_text="Test experience",
        source_system="TEAM_B",
        source_record_id=source_id,
        status="ACTIVE",
        questions=[
            Question(
                question_text="Test question",
                category="DSA",
                difficulty="MEDIUM",
                source_system="TEAM_B",
                source_record_id=f"{source_id}-q1",
            ),
        ],
    )
    db_session.add(interview)
    await db_session.flush()
    return interview


@pytest.mark.asyncio
async def test_get_interview(
    client: AsyncClient, db_session: AsyncSession, seed_all, student_auth_headers
):
    interview = await _seed_interview(db_session)

    response = await client.get(f"{INTERVIEWS_URL}/{interview.id}", headers=student_auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == str(interview.id)
    assert data["role"] == "Software Engineer"
    assert len(data["questions"]) == 1


@pytest.mark.asyncio
async def test_get_interview_not_found(client: AsyncClient, student_auth_headers):
    response = await client.get(f"{INTERVIEWS_URL}/{uuid.uuid4()}", headers=student_auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_interviews_pagination(
    client: AsyncClient, db_session: AsyncSession, seed_all, student_auth_headers
):
    for i in range(15):
        await _seed_interview(db_session, source_id=f"page-{i}")

    response = await client.get(f"{INTERVIEWS_URL}?page=1&size=10", headers=student_auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["total_elements"] == 15
    assert data["total_pages"] == 2
    assert len(data["items"]) == 10
    assert data["has_next"] is True
    assert data["has_previous"] is False


@pytest.mark.asyncio
async def test_list_interviews_filter_difficulty(
    client: AsyncClient, db_session: AsyncSession, seed_all, student_auth_headers
):
    await _seed_interview(db_session, source_id="easy-1", difficulty="EASY")
    await _seed_interview(db_session, source_id="hard-1", difficulty="HARD")

    response = await client.get(f"{INTERVIEWS_URL}?difficulty=EASY", headers=student_auth_headers)
    assert response.status_code == 200

    data = response.json()
    for item in data["items"]:
        assert item["difficulty"] == "EASY"


@pytest.mark.asyncio
async def test_list_interviews_unauthorized(client: AsyncClient):
    response = await client.get(INTERVIEWS_URL)
    assert response.status_code == 403
