import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.study_plan import StudyPlan
from tests.conftest import COMPANY_UUID, STUDENT_UUID, STUDENT_2_UUID

STUDY_PLANS_URL = "/api/v1/study-plans"


def _valid_plan_payload() -> dict:
    return {
        "title": "DSA Preparation Plan",
        "description": "Prepare for technical interviews.",
        "target_company_id": str(COMPANY_UUID),
        "target_role": "Software Engineer",
        "start_date": "2026-10-01",
        "target_date": "2026-12-31",
    }


@pytest.mark.asyncio
async def test_create_study_plan(
    client: AsyncClient, seed_all, student_auth_headers
):
    response = await client.post(
        STUDY_PLANS_URL, json=_valid_plan_payload(), headers=student_auth_headers
    )
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "DSA Preparation Plan"
    assert data["student_id"] == str(STUDENT_UUID)
    assert data["status"] == "ACTIVE"


@pytest.mark.asyncio
async def test_create_study_plan_invalid_dates(
    client: AsyncClient, seed_all, student_auth_headers
):
    payload = _valid_plan_payload()
    payload["start_date"] = "2026-12-31"
    payload["target_date"] = "2026-10-01"

    response = await client.post(
        STUDY_PLANS_URL, json=payload, headers=student_auth_headers
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_study_plan_invalid_company(
    client: AsyncClient, seed_all, student_auth_headers
):
    payload = _valid_plan_payload()
    payload["target_company_id"] = str(uuid.uuid4())

    response = await client.post(
        STUDY_PLANS_URL, json=payload, headers=student_auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_own_study_plan(
    client: AsyncClient, db_session: AsyncSession, seed_all, student_auth_headers
):
    plan = StudyPlan(
        student_id=STUDENT_UUID,
        title="My Plan",
        status="ACTIVE",
    )
    db_session.add(plan)
    await db_session.flush()

    response = await client.get(
        f"{STUDY_PLANS_URL}/{plan.id}", headers=student_auth_headers
    )
    assert response.status_code == 200
    assert response.json()["title"] == "My Plan"


@pytest.mark.asyncio
async def test_get_other_students_plan_forbidden(
    client: AsyncClient, db_session: AsyncSession, seed_all, student_2_auth_headers
):
    plan = StudyPlan(
        student_id=STUDENT_UUID,
        title="Student 1 Plan",
        status="ACTIVE",
    )
    db_session.add(plan)
    await db_session.flush()

    response = await client.get(
        f"{STUDY_PLANS_URL}/{plan.id}", headers=student_2_auth_headers
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_view_any_plan(
    client: AsyncClient, db_session: AsyncSession, seed_all, admin_auth_headers
):
    plan = StudyPlan(
        student_id=STUDENT_UUID,
        title="Student Plan",
        status="ACTIVE",
    )
    db_session.add(plan)
    await db_session.flush()

    response = await client.get(
        f"{STUDY_PLANS_URL}/{plan.id}", headers=admin_auth_headers
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_own_study_plan(
    client: AsyncClient, db_session: AsyncSession, seed_all, student_auth_headers
):
    plan = StudyPlan(
        student_id=STUDENT_UUID,
        title="Old Title",
        status="ACTIVE",
    )
    db_session.add(plan)
    await db_session.flush()

    response = await client.patch(
        f"{STUDY_PLANS_URL}/{plan.id}",
        json={"title": "New Title"},
        headers=student_auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"


@pytest.mark.asyncio
async def test_update_other_students_plan_forbidden(
    client: AsyncClient, db_session: AsyncSession, seed_all, student_2_auth_headers
):
    plan = StudyPlan(
        student_id=STUDENT_UUID,
        title="Private Plan",
        status="ACTIVE",
    )
    db_session.add(plan)
    await db_session.flush()

    response = await client.patch(
        f"{STUDY_PLANS_URL}/{plan.id}",
        json={"title": "Hacked"},
        headers=student_2_auth_headers,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_study_plans_scoped(
    client: AsyncClient, db_session: AsyncSession, seed_all, student_auth_headers
):
    db_session.add(StudyPlan(student_id=STUDENT_UUID, title="Plan A", status="ACTIVE"))
    db_session.add(StudyPlan(student_id=STUDENT_2_UUID, title="Plan B", status="ACTIVE"))
    await db_session.flush()

    response = await client.get(STUDY_PLANS_URL, headers=student_auth_headers)
    assert response.status_code == 200

    data = response.json()
    for item in data["items"]:
        assert item["student_id"] == str(STUDENT_UUID)
