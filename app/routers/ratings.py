from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.utilities.database import get_db
from app.utilities.models import Rating
from app.schemas.ratings_s import RatingCreate, RatingRead
from app.utilities.dependencies import get_current_user

app = APIRouter(
    prefix="/rating",
    tags=["Rating"]
)

@app.post("/", response_model=RatingRead, status_code=status.HTTP_201_CREATED)
def rate_movie(rating: RatingCreate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    db_rating = Rating(**rating.dict(), user_id=current_user.id)
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return db_rating

@app.get("/movie/{movie_id}", response_model=List[RatingRead])
def get_ratings_for_movie(movie_id: int, db: Session = Depends(get_db)):
    ratings = db.query(Rating).filter(Rating.movie_id == movie_id).all()
    return ratings
