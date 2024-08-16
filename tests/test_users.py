import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.utilities.database import Base, get_db
from app.utilities.models import User

# Setting up the database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # Use an in-memory SQLite database
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

# Dependency override for testing
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop the database tables after each test
    Base.metadata.drop_all(bind=engine)

def test_register_user():
    response = client.post(
        "/user/register",
        json={"email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

def test_login_user():
    # Register a user first
    client.post(
        "/user/register",
        json={"email": "test@example.com", "password": "password123"}
    )

    # Now try logging in
    response = client.post(
        "/user/login",
        data={"username": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
