from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Date
from database import Base
from sqlalchemy.orm import relationship
from datetime import datetime


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    password = Column(String)

    periods = relationship("Period", back_populates="user")


class Period(Base):
    __tablename__ = "periods"
    id = Column(Integer, primary_key=True)
    period_name = Column(String)  # sang / chieu / toi

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="periods")

    blocks = relationship("TimeBlock", back_populates="period")


class TimeBlock(Base):
    __tablename__ = "time_blocks"
    id = Column(Integer, primary_key=True)
    time = Column(DateTime, nullable=False)
    block_name = Column(String, nullable=False)
    period_id = Column(Integer, ForeignKey("periods.id"))
    period = relationship("Period", back_populates="blocks")

    blogs = relationship("Blog", back_populates="block")


class Blog(Base):
    __tablename__ = "blogs"
    id = Column(Integer, primary_key=True)
    air_quality = Column(Float)

    block_id = Column(Integer, ForeignKey("time_blocks.id"))
    block = relationship("TimeBlock", back_populates="blogs")


class Predict(Base):
    __tablename__ = "predicts"
    id = Column(Integer, primary_key=True)
    air_quality = Column(Float)

    block_id = Column(Integer, ForeignKey("time_blocks.id"))
    block = relationship("TimeBlock", back_populates="predicts")
