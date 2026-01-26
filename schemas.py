from typing import List
from pydantic import BaseModel, ConfigDict
from typing import Optional


class BlogBase(BaseModel):
    title: str
    body: str


class BlogCreate(BlogBase):
    pass


class BlogUpdate(BlogBase):
    pass


class Blog(BlogBase):
    model_config = ConfigDict(from_attributes=True)


class ShowUser(BaseModel):
    name: str
    email: str
    blogs: List[Blog] = []

    model_config = ConfigDict(from_attributes=True)


class ShowBlog(BaseModel):
    title: str
    body: str
    creator: Optional[ShowUser] = None

    model_config = ConfigDict(from_attributes=True)


class User(BaseModel):
    name: str
    email: str
    password: str


class login(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class TokenData(BaseModel):
    email: Optional[str] = None
