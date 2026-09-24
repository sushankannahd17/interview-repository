import uuid

import pytest
from httpx import AsyncClient

from tests.conftest import ALUMNI_UUID, COMPANY_UUID, STUDENT_UUID

INGEST_URL = "/api/v1/integrations/team-b/interviews"


def _valid_payload(source_id: str = "tb-int-001") -> dict:
    return {
        "source_id": source_id,
        "student_id": str(STUDENT_UUID),
        "company_id": str(COMPANY_UUID),
        "alumni_id": str(ALUMNI_UUID),
        "role": "Software Engineer",
        "interview_date": "2026-09-20",
        "difficulty": "HARD",
        "experience_text": "Great interview experience covering system design.",
        "tips": "Practice distributed systems topics.",
        "questions": [
            {
                "source_id": "tb-q-001",
                "question_text": "Explain TCP vs UDP",
                "category": "NETWORKING",
                "difficulty": "MEDIUM",
                "expected_answer": None,
            },
            {
                "source_id": "tb-q-002",
                "question_text": "Design a URL shortener",
                "category": "SYSTEM_DESIGN",
                "difficulty": "HARD",
                "expected_answer": None,
            },
        ],
    }


@pytest.mark.asyncio
async def test_ingest_interview_success(client: AsyncClient, seed_all, team_b_headers):
    response = await client.post(INGEST_URL, json=_valid_payload(), headers=team_b_headers)
    assert response.status_code == 201

    data = response.json()
    assert data["student_id"] == str(STUDENT_UUID)
    assert data["company_id"] == str(COMPANY_UUID)
    assert data["role"] == "Software Engineer"
    assert data["difficulty"] == "HARD"
    assert len(data["questions"]) == 2


@pytest.mark.asyncio
async def test_ingest_idempotency(client: AsyncClient, seed_all, team_b_headers):
    payload = _valid_payload("tb-int-idem-001")

    r1 = await client.post(INGEST_URL, json=payload, headers=team_b_headers)
    assert r1.status_code == 201
    id_first = r1.json()["id"]

    r2 = await client.post(INGEST_URL, json=payload, headers=team_b_headers)
    assert r2.status_code == 200
    assert r2.json()["id"] == id_first


@pytest.mark.asyncio
async def test_ingest_missing_student(client: AsyncClient, seed_all, team_b_headers):
    payload = _valid_payload("tb-int-miss-stu")
    payload["student_id"] = str(uuid.uuid4())

    response = await client.post(INGEST_URL, json=payload, headers=team_b_headers)
    assert response.status_code == 404
    assert "Student" in response.json()["detail"]


@pytest.mark.asyncio
async def test_ingest_missing_company(client: AsyncClient, seed_all, team_b_headers):
    payload = _valid_payload("tb-int-miss-co")
    payload["company_id"] = str(uuid.uuid4())

    response = await client.post(INGEST_URL, json=payload, headers=team_b_headers)
    assert response.status_code == 404
    assert "Company" in response.json()["detail"]


@pytest.mark.asyncio
async def test_ingest_invalid_difficulty(client: AsyncClient, seed_all, team_b_headers):
    payload = _valid_payload("tb-int-bad-diff")
    payload["difficulty"] = "IMPOSSIBLE"

    response = await client.post(INGEST_URL, json=payload, headers=team_b_headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_ingest_empty_questions(client: AsyncClient, seed_all, team_b_headers):
    payload = _valid_payload("tb-int-no-q")
    payload["questions"] = []

    response = await client.post(INGEST_URL, json=payload, headers=team_b_headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_ingest_no_auth(client: AsyncClient, seed_all):
    response = await client.post(INGEST_URL, json=_valid_payload())
    assert response.status_code == 422  # missing header


@pytest.mark.asyncio
async def test_ingest_wrong_api_key(client: AsyncClient, seed_all):
    response = await client.post(
        INGEST_URL,
        json=_valid_payload(),
        headers={"X-Integration-Key": "wrong-key"},
    )
    assert response.status_code == 401
