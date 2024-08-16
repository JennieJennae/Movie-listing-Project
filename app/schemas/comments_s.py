from pydantic import BaseModel
from typing import Optional

class CommentBase(BaseModel):
    text: str
    movie_id: int

class CommentCreate(CommentBase):
    parent_id: Optional[int] = None

class CommentRead(CommentBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
