# pip install requests geopy plyer python-dotenv
# python main.py --> run

import time
import requests
from geopy.geocoders import Nominatim
from datetime import datetime, timezone
from plyer import notification
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv
import sys
print("Python in use:", sys.version)

# 🔐 Load secrets
load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
RECEIVER_EMAILS = os.getenv("RECEIVER_EMAILS").split(",")



# 📍 Config
city = "Delhi"
interval_seconds = 300  # 5 minutes

# 🌍 Get coordinates
def get_coordinates(city):
    geolocator = Nominatim(user_agent="geoapi")
    location = geolocator.geocode(city)
    return (location.latitude, location.longitude)

# ☁️ Fetch PM2.5 value
def get_pm25(lat, lon):
    url = (
        f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}"
        f"&longitude={lon}&hourly=pm2_5"
    )
    response = requests.get(url)
    if response.status_code != 200:
        print(f"❌ API Error: {response.status_code}")
        return None

    data = response.json()
    # ✅ Fixed deprecated utcnow
    current_hour = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:00")
    try:
        index = data["hourly"]["time"].index(current_hour)
        pm25 = data["hourly"]["pm2_5"][index]
        return pm25
    except:
        print("❌ PM2.5 data not available for this hour.")
        return None

# 🤖 Rule-based suggestion
def rule_based_suggestion(pm25):
    if pm25 <= 50:
        return "Air quality is good. Safe to go outside."
    elif pm25 <= 100:
        return "Moderate air quality. Safe but sensitive people should wear a mask."
    elif pm25 <= 150:
        return "Unhealthy for sensitive groups. Mask recommended."
    elif pm25 <= 200:
        return "Unhealthy. Avoid going outside without a mask."
    else:
        return "Very unhealthy. Stay indoors if possible."

# 📧 Send Email
def send_email(subject, body, receivers):
    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = ", ".join(receivers)
        msg.set_content(body)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SENDER_EMAIL, APP_PASSWORD)
            smtp.send_message(msg)

        print("📧 Email sent successfully.")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# 🔁 Main loop
lat, lon = get_coordinates(city)
print("✅ Setup complete. Starting air quality monitor...\n")

while True:
    print("⏳ Fetching air quality data and generating suggestion...")
    pm25 = get_pm25(lat, lon)

    if pm25 is not None:
        suggestion = rule_based_suggestion(pm25)
        title = "🟢 Air Quality Report"
        message = f"PM2.5: {pm25} µg/m³ in city {city}\nSuggestion: {suggestion}"

        # 🛎️ Popup
        notification.notify(
            title=title,
            message=message,
            timeout=10  # seconds
        )

        # 📧 Email
        send_email(subject=title, body=message, receivers=RECEIVER_EMAILS)

        # 🖨️ Terminal output
        print(title)
        print(message)
    else:
        print("⚠️ Could not fetch air quality data.")

    print(f"⏰ Waiting {interval_seconds} seconds...\n")
    time.sleep(interval_seconds)
