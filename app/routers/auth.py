from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import select
from .. import models, schemas, utils, oauth2
from ..database import get_db

router = APIRouter(
    tags = ['Authentication']
)

@router.post('/login')
def login(user_cred: OAuth2PasswordRequestForm = Depends() ,db: Session = Depends(get_db)):
    user = db.scalar(select(models.User).where(models.User.email == user_cred.username))

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"invalid credentials")

    if not utils.verify(user_cred.password, user.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"invalid credentials")

    #create token
    #return token

    access_token = oauth2.create_access_token(data = {"user_id" : user.id})

    return {"access_token" : access_token, "token_type": "bearer"}