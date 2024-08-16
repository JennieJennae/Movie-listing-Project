import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.utilities.models import Base, Comment, Movie
from app.utilities.database import get_db

# Setup the test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # Using SQLite for simplicity in tests
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency to use the test database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Setup the test client
client = TestClient(app)

# Pytest fixture to create the test database and tear it down after tests
@pytest.fixture(scope="module")
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_comment(setup_db):
    # First, create a movie to comment on
    create_movie_response = client.post(
        "/movie/",
        json={"title": "Test Movie", "description": "A test movie description"},
        headers={"Authorization": "Bearer testtoken"}  # Replace with a real or mock token
    )
    movie_id = create_movie_response.json()["id"]

    # Now create a comment on the movie
    response = client.post(
        "/comment/",
        json={"movie_id": movie_id, "content": "This is a test comment"},
        headers={"Authorization": "Bearer testtoken"}  # Replace with a real or mock token
    )
    assert response.status_code == 201
    assert response.json()["content"] == "This is a test comment"

def test_get_comments_for_movie(setup_db):
    # Assume there is a movie created already, and we are fetching comments for it
    movie_id = 1  # Replace with the actual movie ID from your test DB

    response = client.get(f"/comment/movie/{movie_id}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_reply_to_comment(setup_db):
    # First, create a comment to reply to
    create_movie_response = client.post(
        "/movie/",
        json={"title": "Another Test Movie", "description": "Another test movie description"},
        headers={"Authorization": "Bearer testtoken"}  # Replace with a real or mock token
    )
    movie_id = create_movie_response.json()["id"]

    create_comment_response = client.post(
        "/comment/",
        json={"movie_id": movie_id, "content": "This is a parent comment"},
        headers={"Authorization": "Bearer testtoken"}  # Replace with a real or mock token
    )
    comment_id = create_comment_response.json()["id"]

    # Now reply to the comment
    response = client.post(
        f"/comment/{comment_id}/reply",
        json={"movie_id": movie_id, "content": "This is a reply to the parent comment"},
        headers={"Authorization": "Bearer testtoken"}  # Replace with a real or mock token
    )
    assert response.status_code == 201
    assert response.json()["content"] == "This is a reply to the parent comment"
    assert response.json()["parent_id"] == comment_id
