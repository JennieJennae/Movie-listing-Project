from fastapi import FastAPI, APIRouter, Depends
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from app.routers import movies, users, comments, ratings
from app.utilities import models, database
from app.utilities.models import Movie, User
from app.utilities.database import *


app = FastAPI(
    title= "Jennifer's MovieAPI",
    description= "movie database using FastAPI & Postgres",
    docs_url= "/"
)

models.Base.metadata.create_all(bind=database.engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

while True:   
    try:
        conn = psycopg2.connect(host='localhost', database = 'movielist' , user = 'postgres', password = 'postgres1', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print('Connection to Postgres was successful')
        break
    except Exception as error:
        print('connection failed')
        print("Error: ", error)
        time.sleep(4)


app.include_router(movies.app)
app.include_router(users.app)
app.include_router(comments.app)
app.include_router(ratings.app)
