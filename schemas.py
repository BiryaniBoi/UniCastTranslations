from pydantic import BaseModel
from typing import Optional

class DeviceBase(BaseModel):
    device_token: str
    language: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class DeviceCreate(DeviceBase):
    pass

class Device(DeviceBase):
    id: int

    class Config:
        from_attributes = True

class AlertBase(BaseModel):
    message: str
    language: str

class Alert(AlertBase):
    id: int
    timestamp: str
    translated_message: Optional[str] = None # Added this for completeness, though we'll use AlertDisplay for API output
    severity: Optional[str] = None
    
    class Config:
        from_attributes = True

class AlertDisplay(BaseModel):
    """Schema for displaying alerts in the frontend, including translated content."""
    id: int
    alert_id: str # Original ID from the source (e.g., FEMA)
    message: str # Original message
    translated_message: str # Message in the device's preferred language
    severity: str
    timestamp: str # Formatted timestamp

    class Config:
        from_attributes = True