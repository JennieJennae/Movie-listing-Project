from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.utilities.database import get_db
from app.utilities.models import Comment
from app.schemas.comments_s import CommentCreate, CommentRead
from app.utilities.dependencies import get_current_user

app = APIRouter(
    prefix="/comment",
    tags=["Comment"]
)

@app.post("/", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
def create_comment(comment: CommentCreate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    db_comment = Comment(**comment.dict(), user_id=current_user.id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@app.get("/movie/{movie_id}", response_model=List[CommentRead])
def get_comments_for_movie(movie_id: int, db: Session = Depends(get_db)):
    comments = db.query(Comment).filter(Comment.movie_id == movie_id).all()
    return comments

@app.post("/{comment_id}/reply", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
def reply_to_comment(comment_id: int, reply: CommentCreate, db: Session = Depends(get_db), current_user: int = Depends(get_current_user)):
    parent_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if parent_comment is None:
        raise HTTPException(status_code=404, detail="Parent comment not found")
    db_reply = Comment(**reply.dict(), parent_id=comment_id, user_id=current_user.id)
    db.add(db_reply)
    db.commit()
    db.refresh(db_reply)
    return db_reply
