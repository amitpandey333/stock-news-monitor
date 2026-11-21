"""Instant alerts: SMS through Twilio, or console output when Twilio is not configured."""
from config import ALERT_TO, SMS_ENABLED, TWILIO_FROM, TWILIO_SID, TWILIO_TOKEN


def send_alert(message):
    """Send an alert. Returns a short status string; never crashes the monitor."""
    print(f"[ALERT] {message}")
    if not SMS_ENABLED:
        return "console"
    try:
        from twilio.rest import Client
        Client(TWILIO_SID, TWILIO_TOKEN).messages.create(
            body=message[:300], from_=TWILIO_FROM, to=ALERT_TO)
        return "sms"
    except Exception as exc:  # Twilio raises several exception types
        print(f"[ALERT] SMS failed: {exc}")
        return "failed"
