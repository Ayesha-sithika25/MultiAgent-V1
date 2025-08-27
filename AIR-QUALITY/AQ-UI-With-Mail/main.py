# pip install streamlit requests geopy python-dotenv

# Run with: streamlit run main.py

import streamlit as st
import requests
from geopy.geocoders import Nominatim
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage

# App + Page Settings

st.set_page_config(page_title="Air Quality Notifier", page_icon="🌍")

# Load secrets from .env

load_dotenv()
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
RECEIVER_EMAILS_RAW = os.getenv("RECEIVER_EMAILS")

RECEIVER_EMAILS = []
if RECEIVER_EMAILS_RAW:
    RECEIVER_EMAILS = [e.strip() for e in RECEIVER_EMAILS_RAW.split(",") if e.strip()]

# Core helpers

@st.cache_data(show_spinner=False)
def get_coordinates(city: str):
    """
    Convert a city name to (lat, lon) using Nominatim.
    Cached to avoid rate limits and speed up repeated lookups.
    """
    geolocator = Nominatim(user_agent="aq_notifier_app")
    location = geolocator.geocode(city)
    if not location:
        raise ValueError("City not found. Try 'Delhi, India' or check spelling.")
    return (location.latitude, location.longitude)

def get_pm25(lat: float, lon: float):
    """
    Fetch hourly PM2.5 data and return the value for the current UTC hour
    or the latest available hour as a fallback.
    """
    url = (
        "https://air-quality-api.open-meteo.com/v1/air-quality"
        f"?latitude={lat}&longitude={lon}&hourly=pm2_5"
    )
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    data = r.json()

    times = data["hourly"]["time"]
    values = data["hourly"]["pm2_5"]

    # Current hour in UTC (API uses UTC timestamps)
    
    current_hour = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:00")

    if current_hour in times:
        return values[times.index(current_hour)], current_hour
    else:
        # Fallback: latest available hour
        return values[-1], times[-1]

def rule_based_suggestion(pm25: float) -> str:
    """
    Simple thresholds -> advice.
    """
    if pm25 <= 12:
        return "Good. Generally considered safe with minimal risk."
    elif pm25 <= 35:
        return "Moderate. May cause respiratory irritation in sensitive individuals."
    elif pm25 <= 55.4:
        return "Unhealthy. May cause respiratory irritation in sensitive individuals (children, the elderly, and those with respiratory issues)."
    elif pm25 <= 150.4:
        return "Unhealthy. Can cause more serious health effects, including lung and heart problems.."
    elif pm25 <= 250.4:
        return "Very Unhealthy. Can cause serious health effects for everyone."
    else:
        return "Hazardous. Can cause severe health effects, even life-threatening conditions, Stay indoors if possible."

def format_timestamp(ts: str) -> str:
    """
    Convert 'YYYY-MM-DDTHH:00' UTC string into a clear readable format.
    Example: '2025-08-13T09:00' -> '13 Aug 2025, 09:00 UTC'
    """
    dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M")
    return dt.strftime("%d %b %Y, %H:%M UTC")

def send_email(subject: str, body: str, receivers: list[str]) -> bool:
    """
    Send email via Gmail SMTP over SSL.
    """
    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = ", ".join(receivers)
        msg.set_content(body)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SENDER_EMAIL, APP_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.warning(f"Email not sent: {e}")
        return False

# UI

st.title("🌥😷 Air Quality Notifier")
st.write("Type a city,  click **' *Check Air Quality* '** and get a health suggestion based on PM2.5 value.")

city = st.text_input("City name", value=" ")
email_possible = bool(SENDER_EMAIL and APP_PASSWORD and len(RECEIVER_EMAILS) > 0)
send_email_opt = st.checkbox(
    "Send results via email",
    value=False,
    disabled=not email_possible,
    help="Enable by setting SENDER_EMAIL, APP_PASSWORD and RECEIVER_EMAILS in your .env file."
)

if st.button("Check Air Quality"):
    with st.spinner("Fetching coordinates and air quality..."):
        try:
            lat, lon = get_coordinates(city)
            pm25, ts = get_pm25(lat, lon)
        except Exception as e:
            st.error(f"⚠️ Error: {e}")
        else:
            readable_time = format_timestamp(ts)
            suggestion = rule_based_suggestion(pm25)

            st.success(f"PM2.5 in {city} on {readable_time}: **{pm25} µg/m³**")
            st.info(f"**Suggestion:** {suggestion}")

            if send_email_opt:
                ok = send_email(
                    subject="Air Quality Report",
                    body=(
                        f"City: {city}\n"
                        f"Date & Time (UTC): {readable_time}\n"
                        f"PM2.5: {pm25} µg/m³\n"
                        f"Suggestion: {suggestion}"
                    ),
                    receivers=RECEIVER_EMAILS,
                )
                if ok:
                    st.success("📧 Email sent!")
                else:
                    st.error("❌ Could not send email. Check credentials.")

