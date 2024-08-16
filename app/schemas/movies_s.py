from pydantic import BaseModel
from typing import List, Optional

class MovieBase(BaseModel):
    title: str
    synopsis: str
    director: str
    release_year: int
    genre: list[str]
    starring: list[str]
    duration: int

class MovieCreate(MovieBase):
    pass

class Movie(MovieBase):
    pass

class MovieRead(MovieBase):
    id: int
    owner_id: int

    class Config:
       from_attributes = True
