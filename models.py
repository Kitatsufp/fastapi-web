from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base


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
    period_name = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="periods")
    sensor_blocks = relationship("SensorTimeBlock", back_populates="period")


class SensorTimeBlock(Base):
    __tablename__ = "sensor_time_blocks"

    id = Column(Integer, primary_key=True)
    time = Column(DateTime, nullable=False)
    block_name = Column(String, nullable=False)
    period_id = Column(Integer, ForeignKey("periods.id"))

    period = relationship("Period", back_populates="sensor_blocks")
    sensor_data = relationship(
        "SensorData", back_populates="block", uselist=False)
    prediction_data = relationship(
        "PredictionData", back_populates="block", uselist=False)


class SensorData(Base):
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True)
    iaq = Column(Float, nullable=True)
    tvoc = Column(Float, nullable=True)
    eco2 = Column(Float, nullable=True)
    etoh = Column(Float, nullable=True)
    block_id = Column(Integer, ForeignKey("sensor_time_blocks.id"))

    block = relationship("SensorTimeBlock", back_populates="sensor_data")


class PredictionData(Base):
    __tablename__ = "prediction_data"

    id = Column(Integer, primary_key=True)
    iaq = Column(Float, nullable=True)
    tvoc = Column(Float, nullable=True)
    eco2 = Column(Float, nullable=True)
    etoh = Column(Float, nullable=True)
    block_id = Column(Integer, ForeignKey("sensor_time_blocks.id"))

    block = relationship("SensorTimeBlock", back_populates="prediction_data")
