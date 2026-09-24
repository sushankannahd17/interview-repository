import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.progress import ProgressEntry
from app.models.study_plan import StudyPlan
from tests.conftest import STUDENT_UUID


async def _seed_plan(db_session: AsyncSession, student_id=STUDENT_UUID) -> StudyPlan:
    plan = StudyPlan(
        student_id=student_id,
        title="Test Plan",
        status="ACTIVE",
    )
    db_session.add(plan)
    await db_session.flush()
    return plan


@pytest.mark.asyncio
async def test_create_progress(
    client: AsyncClient, db_session: AsyncSession, seed_all, student_auth_headers
):
    plan = await _seed_plan(db_session)

    response = await client.post(
        f"/api/v1/study-plans/{plan.id}/progress",
        json={"topic": "Binary Search", "status": "NOT_STARTED"},
        headers=student_auth_headers,
    )
    assert response.status_code == 201

    data = response.json()
    assert data["topic"] == "Binary Search"
    assert data["status"] == "NOT_STARTED"
    assert data["completed_at"] is None


@pytest.mark.asyncio
async def test_create_progress_completed_sets_timestamp(
    client: AsyncClient, db_session: AsyncSession, seed_all, student_auth_headers
):
    plan = await _seed_plan(db_session)

    response = await client.post(
        f"/api/v1/study-plans/{plan.id}/progress",
        json={"topic": "Arrays", "status": "COMPLETED"},
        headers=student_auth_headers,
    )
    assert response.status_code == 201
    assert response.json()["completed_at"] is not None


@pytest.mark.asyncio
async def test_update_progress_status_to_completed(
    client: AsyncClient, db_session: AsyncSession, seed_all, student_auth_headers
):
    plan = await _seed_plan(db_session)
    entry = ProgressEntry(
        study_plan_id=plan.id,
        topic="Graphs",
        status="IN_PROGRESS",
    )
    db_session.add(entry)
    await db_session.flush()

    response = await client.patch(
        f"/api/v1/progress/{entry.id}",
        json={"status": "COMPLETED"},
        headers=student_auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["completed_at"] is not None


@pytest.mark.asyncio
async def test_update_progress_status_away_from_completed(
    client: AsyncClient, db_session: AsyncSession, seed_all, student_auth_headers
):
    plan = await _seed_plan(db_session)
    entry = ProgressEntry(
        study_plan_id=plan.id,
        topic="Trees",
        status="IN_PROGRESS",
    )
    db_session.add(entry)
    await db_session.flush()

    await client.patch(
        f"/api/v1/progress/{entry.id}",
        json={"status": "COMPLETED"},
        headers=student_auth_headers,
    )

    response = await client.patch(
        f"/api/v1/progress/{entry.id}",
        json={"status": "IN_PROGRESS"},
        headers=student_auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["completed_at"] is None


@pytest.mark.asyncio
async def test_progress_ownership_forbidden(
    client: AsyncClient, db_session: AsyncSession, seed_all, student_2_auth_headers
):
    plan = await _seed_plan(db_session, student_id=STUDENT_UUID)

    response = await client.post(
        f"/api/v1/study-plans/{plan.id}/progress",
        json={"topic": "Hacking", "status": "NOT_STARTED"},
        headers=student_2_auth_headers,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_progress(
    client: AsyncClient, db_session: AsyncSession, seed_all, student_auth_headers
):
    plan = await _seed_plan(db_session)
    for i in range(5):
        db_session.add(
            ProgressEntry(
                study_plan_id=plan.id,
                topic=f"Topic {i}",
                status="NOT_STARTED",
            )
        )
    await db_session.flush()

    response = await client.get(
        f"/api/v1/study-plans/{plan.id}/progress",
        headers=student_auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["total_elements"] == 5


@pytest.mark.asyncio
async def test_progress_nonexistent_plan(client: AsyncClient, seed_all, student_auth_headers):
    response = await client.post(
        f"/api/v1/study-plans/{uuid.uuid4()}/progress",
        json={"topic": "Test", "status": "NOT_STARTED"},
        headers=student_auth_headers,
    )
    assert response.status_code == 404
