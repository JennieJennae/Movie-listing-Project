import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.utilities.models import Base, Movie
from app.utilities.database import get_db

# Setup the test database (using SQLite for testing)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # Change if needed
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create a test client
client = TestClient(app)

# Pytest fixture to setup and teardown the test database
@pytest.fixture(scope="module")
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_movie(setup_db):
    response = client.post(
        "/movie/",
        json={"title": "Test Movie", "description": "Test movie description"},
        headers={"Authorization": "Bearer testtoken"}  # Ensure this token is valid
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test Movie"

def test_read_movies(setup_db):
    response = client.get("/movie/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

def test_read_one_movie(setup_db):
    # First, create a movie
    create_response = client.post(
        "/movie/",
        json={"title": "Another Test Movie", "description": "Another test movie description"},
        headers={"Authorization": "Bearer testtoken"}  # Replace with a real or mock token
    )
    movie_id = create_response.json()["id"]

    # Then, read the created movie
    response = client.get(f"/movie/{movie_id}")
    assert response.status_code == 200
    assert response.json()["id"] == movie_id

def test_edit_movie(setup_db):
    # First, create a movie
    create_response = client.post(
        "/movie/",
        json={"title": "Movie to Edit", "description": "Edit this movie"},
        headers={"Authorization": "Bearer testtoken"}  # Replace with a real or mock token
    )
    movie_id = create_response.json()["id"]

    # Then, edit the created movie
    response = client.put(
        f"/movie/{movie_id}",
        json={"title": "Edited Movie", "description": "This movie was edited"},
        headers={"Authorization": "Bearer testtoken"}  # Replace with a real or mock token
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Edited Movie"

def test_delete_movie(setup_db):
    # First, create a movie
    create_response = client.post(
        "/movie/",
        json={"title": "Movie to Delete", "description": "Delete this movie"},
        headers={"Authorization": "Bearer testtoken"}  # Replace with a real or mock token
    )
    movie_id = create_response.json()["id"]

    # Then, delete the created movie
    response = client.delete(
        f"/movie/{movie_id}",
        headers={"Authorization": "Bearer testtoken"}  # Replace with a real or mock token
    )
    assert response.status_code == 204

    # Verify the movie is deleted
    get_response = client.get(f"/movie/{movie_id}")
    assert get_response.status_code == 404


