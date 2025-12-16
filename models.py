from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
import datetime

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    device_token = Column(String, unique=True, index=True, nullable=False)
    language = Column(String, default="en")
    # Storing location as simple lat/lon for the demo
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String, unique=True, index=True) # From the source (IPAWS)
    message = Column(String, nullable=False)
    translated_message = Column(String, nullable=True)
    language = Column(String, nullable=False)
    severity = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
