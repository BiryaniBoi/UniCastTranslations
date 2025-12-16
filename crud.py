from sqlalchemy.orm import Session
import models, schemas

# --- Device CRUD ---

def get_device_by_token(db: Session, device_token: str):
    """
    Retrieve a device by its unique token.
    """
    return db.query(models.Device).filter(models.Device.device_token == device_token).first()

def create_device(db: Session, device: schemas.DeviceCreate):
    """
    Create a new device record.
    """
    db_device = models.Device(**device.dict())
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device

def get_all_devices(db: Session):
    """
    Retrieve all registered devices.
    """
    return db.query(models.Device).all()


# --- Alert CRUD ---

def create_alert(db: Session, alert_id: str, message: str, language: str, translated_message: str = None, severity: str = None):
    """
    Create a new alert record.
    """
    db_alert = models.Alert(
        alert_id=alert_id,
        message=message,
        language=language,
        translated_message=translated_message,
        severity=severity
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

def get_alert_by_id(db: Session, alert_id: str):
    """
    Check if an alert with a given ID has already been processed.
    """
    return db.query(models.Alert).filter(models.Alert.alert_id == alert_id).first()
