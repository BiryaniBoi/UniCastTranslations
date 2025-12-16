import datetime

LOG_FILE = "notifications.log"

def send_push_notification(device_token: str, message: str):
    """
    Simulates sending a push notification by writing it to a log file.
    """
    timestamp = datetime.datetime.now().isoformat()
    log_message = f"[{timestamp}] TO: {device_token} MESSAGE: '{message}'\n"
    
    # Print to console for immediate feedback
    print(f"--- SENDING NOTIFICATION (see {LOG_FILE}) ---")
    print(f"To: {device_token}")
    print(f"Message: '{message}'")
    
    # Append to the log file
    try:
        with open(LOG_FILE, "a") as f:
            f.write(log_message)
    except IOError as e:
        print(f"--- ERROR: Could not write to log file {LOG_FILE}: {e} ---")