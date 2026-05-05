from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class SensorDataBase(BaseModel):
    iaq: Optional[float] = None
    tvoc: Optional[float] = None
    eco2: Optional[float] = None
    etoh: Optional[float] = None


class SensorDataCreate(SensorDataBase):
    pass


class SensorData(SensorDataBase):
    model_config = ConfigDict(from_attributes=True)


class SensorDataResponse(BaseModel):
    time: datetime
    period: str
    block: str
    iaq: Optional[float] = None
    tvoc: Optional[float] = None
    eco2: Optional[float] = None
    etoh: Optional[float] = None
    model_config = ConfigDict(from_attributes=True)


class PredictionDataBase(BaseModel):
    iaq: Optional[float] = None
    tvoc: Optional[float] = None
    eco2: Optional[float] = None
    etoh: Optional[float] = None


class PredictionDataCreate(PredictionDataBase):
    pass


class PredictionData(PredictionDataBase):
    model_config = ConfigDict(from_attributes=True)


class PredictionDataResponse(BaseModel):
    time: datetime
    period: str
    block: str
    iaq: Optional[float] = None
    tvoc: Optional[float] = None
    eco2: Optional[float] = None
    etoh: Optional[float] = None
    model_config = ConfigDict(from_attributes=True)


class User(BaseModel):
    name: str
    email: str
    password: str


class ShowUser(BaseModel):
    name: str
    email: str
    model_config = ConfigDict(from_attributes=True)


class Login(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None
    id: Optional[int] = None


class DailySensorMetrics(BaseModel):
    time: str
    iaq: Optional[float] = None
    tvoc: Optional[float] = None
    eco2: Optional[float] = None
    etoh: Optional[float] = None


class DailyPredictionMetrics(BaseModel):
    time: str
    iaq: Optional[float] = None
    tvoc: Optional[float] = None
    eco2: Optional[float] = None
    etoh: Optional[float] = None
