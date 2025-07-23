import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import get_db
from app.db.base import Base
from app.core.config import settings

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True
)

# Create test session factory
TestSessionLocal = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@pytest.fixture(scope="session")
async def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def db_session():
    """Create a test database session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client(db_session):
    """Create a test client."""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()

@pytest.fixture
async def auth_headers(client: AsyncClient):
    """Create authentication headers for testing."""
    # Register a test user
    user_data = {
        "email": "testauth@example.com",
        "username": "testauth",
        "password": "testpassword123"
    }
    await client.post("/api/v1/users/register", json=user_data)
    
    # Login to get token
    login_data = {
        "email": "testauth@example.com",
        "password": "testpassword123"
    }
    response = await client.post("/api/v1/users/login", json=login_data)
    token = response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
async def test_user_id(client: AsyncClient):
    """Create a test user and return its ID."""
    user_data = {
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "testpassword123"
    }
    response = await client.post("/api/v1/users/register", json=user_data)
    return response.json()["id"]
