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
        message = raw_alert['message']
        severity = raw_alert['severity']

        if crud.get_alert_by_id(db, alert_id):
            # We've already processed this alert, so we can skip it.
            # For a demo, let's just print and continue.
            # In a real app, you might stop here if alerts are chronological.
            continue

        print(f"Processing new alert: {alert_id}")
        
        # Save the original English alert
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
    """
    try:
        # We can add parameters here, like $top=5 to get only the 5 most recent.
        response = requests.get(f"{FEMA_API_URL}?$top=5")
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx) 
        
        data = response.json()
        fema_alerts = data.get("IpawsArchived", [])
        
        # Format the complex FEMA object into our simple dictionary
        formatted_alerts = []
        for alert in fema_alerts:
            # Skip alerts that don't have message text
            if not alert.get("messageText"):
                continue

            formatted_alerts.append({
                "id": alert.get("id", "UNKNOWN_ID"),
                "message": alert.get("messageText", ""),
                "severity": alert.get("severity", "Unknown"),
            })
        return formatted_alerts

    except requests.exceptions.RequestException as e:
        print(f"\n--- ERROR: Could not fetch alerts from FEMA API: {e} ---\n")
        return [] # Return an empty list to prevent crashes