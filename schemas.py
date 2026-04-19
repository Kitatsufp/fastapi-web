from typing import List
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from datetime import date


class BlogBase(BaseModel):
    air_quality: float


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
    id: int
    air_quality: float
    timestamp: datetime
    period: str
    block: str

    model_config = ConfigDict(from_attributes=True)


class User(BaseModel):
    name: str
    email: str
    password: str


class Login(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None
    id: int | None = None


class PredictionBase(BaseModel):
    value: float


class PredictionCreate(PredictionBase):
    pass


class Prediction(PredictionBase):
    id: int
    date: date
    step: int
    type: str  # "init" | "realtime"

    model_config = ConfigDict(from_attributes=True)
