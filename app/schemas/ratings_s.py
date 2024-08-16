from pydantic import BaseModel
from typing import Optional

class RatingBase(BaseModel):
    movie_id: int
    rating: int

class RatingCreate(RatingBase):
    pass

class RatingRead(RatingBase):
    id: int
    user_id: int

    class Config:
       from_attributes = True
