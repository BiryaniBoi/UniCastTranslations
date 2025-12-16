from sqlalchemy.orm import Session
import requests
import crud
from translation_service import translate_text
from notifier import send_push_notification

# The OpenFEMA API endpoint for past IPAWS alerts
FEMA_API_URL = "https://www.fema.gov/api/open/v1/IpawsArchivedAlerts"

def fetch_and_process_alerts(db: Session):
    """
    Main function to orchestrate the alert processing workflow.
    """
    print("\n--- Checking for new alerts from FEMA API... ---")
    
    raw_alerts = _fetch_alerts_from_source()
    if not raw_alerts:
        print("--- No new alerts found or API call failed. ---")
        return

    for raw_alert in raw_alerts:
        alert_id = raw_alert['id']
        # Skip if the alert ID is null or empty
        if not alert_id:
            continue

        message = raw_alert['message']
        severity = raw_alert['severity']

        if crud.get_alert_by_id(db, alert_id):
            continue

        print(f"Processing new alert: {alert_id}")
        
        crud.create_alert(db, alert_id=alert_id, message=message, language="en", severity=severity)

        devices = crud.get_all_devices(db)
        for device in devices:
            final_message = message
            if device.language != "en":
                final_message = translate_text(message, device.language)
            
            send_push_notification(device.device_token, final_message)
    
    print("--- Finished checking for alerts. ---")


def _fetch_alerts_from_source() -> list:
    """
    Fetches data from the OpenFEMA API for past IPAWS alerts.
    This is the definitive live version and does not contain demo alerts.
    """
    try:
        # Fetch the 10 most recent alerts that have a messageText
        response = requests.get(f"{FEMA_API_URL}?$top=10&$filter=messageText ne null")
        response.raise_for_status()
        
        data = response.json()
        fema_alerts = data.get("IpawsArchivedAlerts", [])
        
        formatted_alerts = []
        for alert in fema_alerts:
            # Ensure the essential fields are present before adding
            if alert.get("id") and alert.get("messageText"):
                formatted_alerts.append({
                    "id": alert.get("id"),
                    "message": alert.get("messageText"),
                    "severity": alert.get("severity", "Unknown"),
                })
        # Reverse the list so that when processed, they are ingested oldest-first
        return formatted_alerts[::-1]

    except requests.exceptions.RequestException as e:
        print(f"\n--- ERROR: Could not fetch alerts from FEMA API: {e} ---\n")
        return []