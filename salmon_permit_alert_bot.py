# salmon_permit_alert_bot.py
# Automatically checks Middle Fork Salmon River permit availability and sends email/SMS alerts.

import requests
from bs4 import BeautifulSoup
from email.message import EmailMessage
import smtplib
from datetime import datetime
import os

# CONFIG - Replace with environment variables or secrets in deployment
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "ianlrvd@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "JulioRod44!")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "ianlrvd@gmail.com")
SMS_GATEWAY = os.getenv("SMS_GATEWAY", "1234567890@vtext.com")
PERMIT_URL = "https://www.recreation.gov/permits/234623"


def check_availability():
    try:
        response = requests.get(PERMIT_URL, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        available_dates = []

        for tag in soup.find_all(attrs={"aria-label": True}):
            label = tag["aria-label"]
            if "Available" in label:
                available_dates.append(label.split(" - ")[0])

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
