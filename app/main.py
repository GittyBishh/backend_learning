from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange

from sqlalchemy.orm import Session
from . import models, schemas
from .database import engine, get_db

# Creates all tables registered on the DeclarativeBase metadata
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

my_posts = [{"title": "title 1", "content": "content 1", "id": 1},
            {"title": "food", "content": "pizza", "id": 2}]

def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p

def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i
    return None

@app.get("/")
async def root():
    return {"message": "Hello Word"}

# @app.get("/sqlalchemy")
# def test_posts(db: Session = Depends(get_db)):

#     posts = db.query(models.Post).all()
#     return {"data": posts}

@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    # print(posts)
    posts = db.query(models.Post).all()
    return posts

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post : schemas.Post, db: Session = Depends(get_db)):
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, (post.title, post.content, post.published))
    # new_post = cursor.fetchone()

    # conn.commit()
    
    
    new_post = models.Post(**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

# @app.get("/posts/latest")
# def get_latest_post():
#     post = my_posts[len(my_posts)-1]
#     return {"details": post}

from sqlalchemy import select
@app.get("/posts/{id}")
def get_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts WHERE id = %s """, (str(id),))
    # post=cursor.fetchone()
    # # print(post)
    # # post = find_post(id)
    # if not post:
    #     # response.status_code = status.HTTP_404_NOT_FOUND
    #     # return {"message": f"post with id : {id} not found"}
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
    #                         detail = f"post with id : {id} was not found")

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
def delete_post(id : int):

    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id),))
    deleted_post = cursor.fetchone()
    conn.commit()

    if deleted_post ==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail = f"post with id : {id} was not found")

    # index = find_index_post(id)
    # if index == None:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
    #                         detail = f"post with id : {id} was not found")
    # my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id : int, post: schemas.Post):

    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", (post.title, post.content, post.published, str(id)))

    updated_post = cursor.fetchone()
    conn.commit() 
    if updated_post == None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail = f"post with id : {id} was not found")

    # index = find_index_post(id)
    # # if index == None:
    # #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
    # #                         detail = f"post with id : {id} was not found")
    # post_dict = post.model_dump()
    # post_dict['id'] = id
    # my_posts[index] = post_dict
    return updated_post