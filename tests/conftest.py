import uuid
from collections.abc import AsyncGenerator
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.database import get_db
from app.main import app
from app.models import (  # noqa: F401
    Company,
    InterviewExperience,
    PlacedAlumni,
    ProgressEntry,
    Question,
    Student,
    StudyPlan,
)
from app.models.base import Base

TEST_DATABASE_URL = settings.DATABASE_URL

STUDENT_UUID = uuid.UUID("11111111-1111-1111-1111-111111111111")
STUDENT_2_UUID = uuid.UUID("22222222-2222-2222-2222-222222222222")
ADMIN_UUID = uuid.UUID("33333333-3333-3333-3333-333333333333")
COMPANY_UUID = uuid.UUID("44444444-4444-4444-4444-444444444444")
ALUMNI_UUID = uuid.UUID("55555555-5555-5555-5555-555555555555")


def create_test_token(user_id: uuid.UUID, role: str, email: str = "test@test.com") -> str:
    payload = {
        "sub": str(user_id),
        "role": role,
        "email": email,
        "exp": int(datetime(2099, 1, 1, tzinfo=timezone.utc).timestamp()),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture(scope="session")
async def engine():
    eng = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest_asyncio.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def student_token() -> str:
    return create_test_token(STUDENT_UUID, "student", "student@test.com")


@pytest.fixture
def student_2_token() -> str:
    return create_test_token(STUDENT_2_UUID, "student", "student2@test.com")


@pytest.fixture
def admin_token() -> str:
    return create_test_token(ADMIN_UUID, "admin", "admin@test.com")


@pytest.fixture
def student_auth_headers(student_token: str) -> dict:
    return {"Authorization": f"Bearer {student_token}"}


@pytest.fixture
def student_2_auth_headers(student_2_token: str) -> dict:
    return {"Authorization": f"Bearer {student_2_token}"}


@pytest.fixture
def admin_auth_headers(admin_token: str) -> dict:
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def team_b_headers() -> dict:
    return {"X-Integration-Key": settings.TEAM_B_API_KEY}


@pytest_asyncio.fixture
async def seed_student(db_session: AsyncSession) -> Student:
    student = Student(
        id=STUDENT_UUID,
        external_id="ext-student-001",
        name="Test Student",
        email="student@test.com",
        role="student",
    )
    db_session.add(student)
    await db_session.flush()
    return student


@pytest_asyncio.fixture
async def seed_student_2(db_session: AsyncSession) -> Student:
    student = Student(
        id=STUDENT_2_UUID,
        external_id="ext-student-002",
        name="Test Student 2",
        email="student2@test.com",
        role="student",
    )
    db_session.add(student)
    await db_session.flush()
    return student


@pytest_asyncio.fixture
async def seed_company(db_session: AsyncSession) -> Company:
    company = Company(
        id=COMPANY_UUID,
        name="Test Company",
        industry="Technology",
        website="https://testcompany.com",
    )
    db_session.add(company)
    await db_session.flush()
    return company


@pytest_asyncio.fixture
async def seed_alumni(db_session: AsyncSession, seed_company: Company) -> PlacedAlumni:
    alumni = PlacedAlumni(
        id=ALUMNI_UUID,
        name="Test Alumni",
        graduation_year=2023,
        company_id=seed_company.id,
        role_at_company="Senior Engineer",
    )
    db_session.add(alumni)
    await db_session.flush()
    return alumni


@pytest_asyncio.fixture
async def seed_all(seed_student, seed_student_2, seed_company, seed_alumni):
    return {
        "student": seed_student,
        "student_2": seed_student_2,
        "company": seed_company,
        "alumni": seed_alumni,
    }
