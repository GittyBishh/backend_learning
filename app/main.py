from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional, List
from random import randrange

from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI() 


import psycopg
from psycopg.rows import dict_row
import time

while True:
    try:
        conn = psycopg.connect(
            host='localhost',
            dbname='fastapi_learning',
            user='postgres',
            password='mypasspostgres',
            row_factory=dict_row
        )
        cursor = conn.cursor()
        print("Database connection was succesfull!")
        break
    except Exception as error:
        print("Connecting to database failed")
        print("Error: ", error)
        time.sleep(2)

@app.get("/")
def root():
    return {"message" : "hello world"}

@app.get("/posts", response_model=List[schemas.Post])
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts

@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post : schemas.PostCreate, db: Session = Depends(get_db)):
    
    
    new_post = models.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

from sqlalchemy import select
@app.get("/posts/{id}", response_model=schemas.Post)
def get_post(id: int, db: Session = Depends(get_db)):

    # 1. Build the select statement and execute it to fetch one post
    post = db.scalar(select(models.Post).where(models.Post.id == id))

    # 2. Handle the 404 case if the post doesn't exist
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found"
        )

    print(post)
    return post

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id : int, db: Session = Depends(get_db)):

    post = db.scalar(select(models.Post).where(models.Post.id == id))
    
    # 2. Check if the post exists
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} does not exist"
        )
    
    # 3. Delete and commit
    db.delete(post)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}", response_model=schemas.Post)
def update_post(id : int, updated_post: schemas.PostBase, db: Session = Depends(get_db)):
    post_query = select(models.Post).where(models.Post.id == id)
    post = db.scalar(post_query)
    
    # 2. Check if the post exists
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} does not exist"
        )
    
    # 3. Update attributes using Pydantic's model_dump()
    for key, value in updated_post.model_dump().items():
        setattr(post, key, value)
        
    # 4. Commit changes to the database
    db.commit()
    db.refresh(post)
    return updated_post