import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.utilities.database import Base, get_db
from app.utilities.models import Rating, User, Movie
from app.schemas.ratings_s import RatingCreate
from app.utilities.dependencies import get_current_user

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
    
    # Insert a test user and movie
    db = TestingSessionLocal()
    user = User(email="test@example.com", hashed_password="hashedpassword")
    db.add(user)
    db.commit()
    db.refresh(user)
    
    movie = Movie(id=1, title="Test Movie", description="A test movie")
    db.add(movie)
    db.commit()
    db.refresh(movie)
    
    yield
    
    # Drop the database tables after each test
    Base.metadata.drop_all(bind=engine)

def test_rate_movie():
    # Simulate user authentication by providing a valid user ID
    app.dependency_overrides[get_current_user] = lambda: User(id=1, email="test@example.com", hashed_password="hashedpassword")

    response = client.post(
        "/rating/",
        json={"movie_id": 1, "rating": 5, "comment": "Great movie!"}
    )
    assert response.status_code == 201
    assert response.json()["rating"] == 5
    assert response.json()["comment"] == "Great movie!"

def test_get_ratings_for_movie():
    # Simulate user authentication by providing a valid user ID
    app.dependency_overrides[get_current_user] = lambda: User(id=1, email="test@example.com", hashed_password="hashedpassword")

    # First, rate the movie
    client.post(
        "/rating/",
        json={"movie_id": 1, "rating": 5, "comment": "Great movie!"}
    )

    response = client.get("/rating/movie/1")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["rating"] == 5
    assert response.json()[0]["comment"] == "Great movie!"
