from pydantic import BaseModel
from typing import Optional, List

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
    translated_message: Optional[str] = None
    severity: Optional[str] = None
    
    class Config:
        from_attributes = True

class AlertDisplay(BaseModel):
    """Schema for displaying alerts in the frontend."""
    id: int
    alert_id: str
    message: str
    translated_message: str
    severity: str
    timestamp: str

    class Config:
        from_attributes = True

# New schemas for the translation endpoint
class TranslationRequest(BaseModel):
    texts: List[str]
    target_lang: str

class TranslationResponse(BaseModel):
    translations: List[str]
