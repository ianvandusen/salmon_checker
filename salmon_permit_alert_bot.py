# salmon_permit_alert_bot.py
# Automatically checks Middle Fork Salmon River permit availability and sends email/SMS alerts.

import requests
from bs4 import BeautifulSoup
from email.message import EmailMessage
import smtplib
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# CONFIG - Values stored in .env (not hardcoded)
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
SMS_GATEWAY = os.getenv("SMS_GATEWAY")
PERMIT_URL = "https://www.recreation.gov/permits/234623"

def check_availability():
    try:
        response = requests.get(PERMIT_URL, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        available_dates = []

        # Set range: from today to Oct 8 this year
        today = datetime.now().date()
        end_date = datetime(today.year, 10, 8).date()

        for tag in soup.find_all(attrs={"aria-label": True}):
            label = tag["aria-label"]
            print(f"[{datetime.now()}] Found aria-label: {label}")  # DEBUG
            if "Available" in label:
                try:
                    date_part = label.split(" - ")[0].strip()
                    parsed_date = datetime.strptime(date_part, "%A, %B %d, %Y").date()
                    if today <= parsed_date <= end_date:
                        available_dates.append(date_part)
                except Exception as e:
                    print(f"[{datetime.now()}] Failed to parse label: {label} - {e}")

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

    date_list = '\n'.join(dates)
    body = f"\U0001F389 Available Dates:\n{date_list}\n\nBook ASAP: {PERMIT_URL}\nChecked: {datetime.now()}"
    msg.set_content(body)

    print(f"[{datetime.now()}] Sending alert to {msg['To']} with body:\n{body}")  # DEBUG

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
