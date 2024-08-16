from fastapi import FastAPI, Depends, HTTPException, APIRouter, logger, status
from sqlalchemy.orm import Session

from typing import List
from fastapi import logger

from app.utilities.database import get_db
from app.utilities.models import Movie
from app.schemas.movies_s import MovieCreate, MovieRead
from app.utilities.dependencies import get_current_user


app = APIRouter(
    prefix="/movie",
    tags=["Movie"]
)

@app.get("/", response_model=List[MovieRead])
def read_movies(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    movies = db.query(Movie).offset(skip).limit(limit).all()
    return movies

@app.get("/{movie_id}",response_model=MovieRead)
def read_one_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

@app.post("/", response_model=MovieRead, status_code=status.HTTP_201_CREATED)
def create_a_movie(movie: MovieCreate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    db_movie = Movie(**movie.dict(), owner_id=current_user.id)
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    logger.info(f"Movie created: {movie.title} ({movie.release_year})")
    return db_movie

@app.put("/{movie_id}",response_model=MovieRead)
def edit_a_movie(movie_id: int, movie: MovieCreate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    db_movie = db.query(Movie).filter(Movie.id == movie_id, Movie.owner_id == current_user.id).first()
    if db_movie is None:
        raise HTTPException(status_code=404, detail="Movie not found or not authorized")
    for key, value in movie.dict().items():
        setattr(db_movie, key, value)
    db.commit()
    db.refresh(db_movie)
    return db_movie

@app.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_a_movie(movie_id: int, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    db_movie = db.query(Movie).filter(Movie.id == movie_id, Movie.owner_id == current_user.id).first()
    if db_movie is None:
        raise HTTPException(status_code=404, detail="Movie not found or not authorized")
    db.delete(db_movie)
    db.commit()
    return


