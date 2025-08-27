import streamlit as st
import requests
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage
import time as time_module

# ----------------------------
# Load environment variables
# ----------------------------
load_dotenv()
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")

# ----------------------------
# Functions (same as before)
# ----------------------------
def get_coordinates(city):
    geolocator = Nominatim(user_agent="air_quality_app")
    location = geolocator.geocode(city)
    if not location:
        raise ValueError("City not found.")
    return location.latitude, location.longitude

def get_pm25(lat, lon):
    url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&hourly=pm2_5"
    response = requests.get(url)
    data = response.json()
    pm25 = data["hourly"]["pm2_5"][0]
    timestamp = data["hourly"]["time"][0]
    return pm25, timestamp

def format_timestamp(ts):
    dt = datetime.fromisoformat(ts)
    return dt.strftime("%I:%M %p, %d %b %Y")

def rule_based_suggestion(pm25):
    if pm25 <= 12:
        return "Air quality is good. Enjoy outdoor activities!"
    elif pm25 <= 35:
        return "Air quality is moderate. Sensitive people should limit outdoor exertion."
    elif pm25 <= 55:
        return "Air quality is unhealthy for sensitive people. Reduce prolonged outdoor activity."
    elif pm25 <= 150:
        return "Air quality is unhealthy. Avoid outdoor activities if possible."
    else:
        return "Air quality is very unhealthy or hazardous. Stay indoors!"

def send_email(subject, body, receivers):
    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = ", ".join(receivers)
        msg.set_content(body)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.send_message(msg)

        return True
    except Exception as e:
        print("Email error:", e)
        return False

# ----------------------------
# Streamlit Page Function
# ----------------------------
def air_quality_app():
    st.write("Type a city and a duration in minutes. The app will keep updating until time ends.")

    city = st.text_input("City name", value=" ")
    duration_minutes = st.number_input("Duration (minutes)", min_value=1, max_value=1440, value=1)

    # User enters their email to receive report
    receiver_email_input = st.text_input("Your Email", value="")

    email_possible = bool(SENDER_EMAIL and APP_PASSWORD)
    send_email_opt = st.checkbox(
        "Send results via email",
        value=False,
        disabled=not email_possible,
        help="A mail including the final result will be sent to the email you entered above."
    )

    if st.button("Start Monitoring"):
        try:
            lat, lon = get_coordinates(city)
        except Exception as e:
            st.error(f"⚠️ Error: {e}")
        else:
            start_time = datetime.now()
            end_time = start_time + timedelta(minutes=duration_minutes)
            placeholder = st.empty()

            final_pm25 = None
            final_readable_time = None
            final_suggestion = None

            while datetime.now() < end_time:
                try:
                    pm25, ts = get_pm25(lat, lon)
                    readable_time = format_timestamp(ts)
                    suggestion = rule_based_suggestion(pm25)

                    # Store final values for sending later
                    final_pm25 = pm25
                    final_readable_time = readable_time
                    final_suggestion = suggestion

                    # Update the display
                    with placeholder.container():
                        st.success(f"PM2.5 in {city} on **{readable_time}**: *{pm25} µg/m³*")
                        st.info(f"Suggestion : **{suggestion}**")
                        st.write(f"Next update in {duration_minutes} minutes. Monitoring until **{end_time.strftime('%I:%M %p')}**.")

                except Exception as e:
                    st.error(f"⚠️ Error fetching data: {e}")

                time_module.sleep(60)  # wait 1 minute before next check

            # When monitoring ends
            with placeholder.container():
                st.warning(f"⏳ Time is **{end_time.strftime('%I:%M %p')}** , Your monitoring session ended, try again!")

            # Send email only once at the end to the user-provided address
            if send_email_opt and final_pm25 is not None and receiver_email_input.strip():
                ok = send_email(
                    subject="Final Air Quality Report",
                    body=(
                        f"City: {city}\n"
                        f"Date & Time: {final_readable_time}\n"
                        f"Final PM2.5: {final_pm25} µg/m³\n"
                        f"Suggestion: {final_suggestion}"
                    ),
                    receivers=[receiver_email_input.strip()],
                )

                if ok:
                    st.success(f"📧 Final email sent to {receiver_email_input.strip()}!")
                else:
                    st.error("❌ Could not send email. Check credentials.")
