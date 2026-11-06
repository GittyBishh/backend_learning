from pydantic import BaseModel, ConfigDict, EmailStr
import datetime
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    ...

class Post(PostBase):
    id : int
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)
