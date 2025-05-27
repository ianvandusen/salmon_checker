# salmon_permit_alert_bot.py
import requests
from email.message import EmailMessage
import smtplib
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
SMS_GATEWAY = os.getenv("SMS_GATEWAY")

PERMIT_ID = "234623"
API_URL = f"https://www.recreation.gov/api/permititinerary/availability/product/{PERMIT_ID}"
PERMIT_WEB_URL = f"https://www.recreation.gov/permits/{PERMIT_ID}"

def check_availability():
    try:
        today = datetime.now().date()
        end_date = datetime(today.year, 10, 8).date()
        available_dates = []

        # API expects date range in format YYYY-MM-DD
        params = {
            "start_date": today.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }
        response = requests.get(API_URL, params=params, timeout=10)
        data = response.json()

        for date_str, day_info in data.get("availability", {}).items():
            if day_info.get("status") == "Available":
                parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                if today <= parsed_date <= end_date:
                    available_dates.append(parsed_date.strftime("%A, %B %d, %Y"))

        return available_dates
    except Exception as e:
        print(f"[{datetime.now()}] Error checking availability: {e}")
        return []

def send_alert(dates):
    msg = EmailMessage()
    msg['Subject'] = "\U0001F6A8 Middle Fork Salmon Permit AVAILABLE!"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = [RECIPIENT_EMAIL]
    if SMS_GATEWAY:
        msg['To'].append(SMS_GATEWAY)

    body = f"\U0001F389 Available Dates:\n" + "\n".join(dates) + f"\n\nBook here: {PERMIT_WEB_URL}\nChecked: {datetime.now()}"
    msg.set_content(body)

    print(f"[{datetime.now()}] Sending alert:\n{body}")  # DEBUG

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"[{datetime.now()}] Notification sent!")
    except Exception as e:
        print(f"[{datetime.now()}] Error sending notification: {e}")

def main():
    available_dates = check_availability()
    if available_dates:
        send_alert(available_dates)
    else:
        print(f"[{datetime.now()}] No permits available.")

if __name__ == "__main__":
    main()
