# salmon_permit_alert_bot.py
# Automatically checks Middle Fork Salmon River permit availability and sends email/SMS alerts using the Recreation.gov API.

import requests
from email.message import EmailMessage
import smtplib
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# CONFIG - Values stored in .env (not hardcoded)
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
SMS_GATEWAY = os.getenv("SMS_GATEWAY")
PERMIT_ID = "234623"
PERMIT_WEB_URL = f"https://www.recreation.gov/permits/{PERMIT_ID}"
API_URL = f"https://www.recreation.gov/api/permititinerary/availability/product/{PERMIT_ID}"

# Date range config (optionally override with env vars)
START_DATE = datetime.now().date()
END_DATE = datetime(datetime.now().year, 10, 8).date()

def check_availability():
    try:
        available_dates = []

        params = {
            "start_date": START_DATE.strftime("%Y-%m-%d"),
            "end_date": END_DATE.strftime("%Y-%m-%d")
        }
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(API_URL, params=params, headers=headers, timeout=10)

        try:
            data = response.json()
        except Exception as json_err:
            print(f"[{datetime.now()}] JSON decode error: {json_err}")
            print(f"[{datetime.now()}] Response text: {response.text[:500]}...")
            return []

        print(f"[{datetime.now()}] Fetched data preview: {str(data)[:500]}...")

        for date_str, info in data.get("availability", {}).items():
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()

            if START_DATE <= parsed_date <= END_DATE:
                if info.get("status") == "Available":
                    available_dates.append(parsed_date.strftime("%A, %B %d, %Y"))

                if "daily_availability" in info:
                    for segment in info["daily_availability"].values():
                        if segment.get("status") == "Available":
                            available_dates.append(parsed_date.strftime("%A, %B %d, %Y"))

        return sorted(set(available_dates))
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

    print(f"[{datetime.now()}] Sending alert:\n{body}")

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
