from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import time
import threading
from typing import List

import crud
from models import Base, Alert as DBAlert # Alias models.Alert to DBAlert to avoid conflict with schemas.Alert
from schemas import DeviceCreate, Device, AlertDisplay
from database import SessionLocal, engine, get_db
from ingestor import fetch_and_process_alerts
from translation_service import translate_text # Import the translation service

# Create the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Emergency Alert Service API",
    description="A demo API for a multilingual emergency alert system.",
    version="0.1.0"
)

# --- CORS Configuration ---
origins = [
    "http://localhost",
    "http://localhost:8001", # Local frontend for development
    "http://cs.shschools.org", # Deployed frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Background Task for Alert Ingestion ---

def run_alert_ingestor():
    """
    This function runs in a separate thread and periodically checks for new alerts.
    """
    db = SessionLocal()
    while True:
        try:
            fetch_and_process_alerts(db)
        except Exception as e:
            print(f"An error occurred in the alert ingestor: {e}")
        # Wait for 60 seconds before checking again
        time.sleep(60)

@app.on_event("startup")
def startup_event():
    """
    On application startup, start the background thread for the alert ingestor.
    """
    thread = threading.Thread(target=run_alert_ingestor, daemon=True)
    thread.start()


# --- API Endpoints ---

@app.get("/", tags=["Status"])
def read_root():
    """
    A simple endpoint to confirm the API is running.
    """
    return {"status": "ok"}

@app.post("/register/", response_model=Device, tags=["Devices"])
def register_device(device: DeviceCreate, db: Session = Depends(get_db)):
    """
    Register a new device to receive notifications.
    If the device token already exists, it will be updated with the new language.
    """
    db_device = crud.get_device_by_token(db, device_token=device.device_token)
    if db_device:
        # Simple update logic for the demo
        db_device.language = device.language
        db_device.latitude = device.latitude
        db_device.longitude = device.longitude
        db.commit()
        db.refresh(db_device)
        return db_device
    return crud.create_device(db=db, device=device)

@app.get("/devices/", response_model=List[Device], tags=["Devices"])
def get_all_devices(db: Session = Depends(get_db)):
    """
    Retrieve a list of all registered devices.
    """
    return crud.get_all_devices(db)

@app.get("/alerts/me/{device_token}", response_model=List[AlertDisplay], tags=["Alerts"])
def get_alerts_for_device(device_token: str, db: Session = Depends(get_db)):
    """
    Retrieve recent alerts for a specific device, translated to its preferred language.
    """
    device = crud.get_device_by_token(db, device_token=device_token)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    # Fetch a few recent alerts (e.g., the last 5)
    recent_db_alerts = db.query(DBAlert).order_by(DBAlert.timestamp.desc()).limit(5).all()

    alerts_for_display: List[AlertDisplay] = []
    for db_alert in recent_db_alerts:
        translated_message = db_alert.message # Start with original message

        # Only translate if the device's language is not English
        if device.language != "en":
            # Call the translation service
            translated_message = translate_text(db_alert.message, device.language)
        
        alerts_for_display.append(AlertDisplay(
            id=db_alert.id,
            alert_id=db_alert.alert_id,
            message=db_alert.message,
            translated_message=translated_message,
            severity=db_alert.severity,
            timestamp=db_alert.timestamp.isoformat() # Convert datetime to string
        ))
    
    return alerts_for_display