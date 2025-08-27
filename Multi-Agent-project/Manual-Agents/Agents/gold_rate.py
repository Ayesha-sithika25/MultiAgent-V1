import streamlit as st
import yfinance as yf
from plyer import notification
from datetime import datetime, timedelta
import pytz
import time as time_module
import os
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage

# ----------------------------
# Load environment variables
# ----------------------------
load_dotenv()
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")

# ----------------------------
# Config
# ----------------------------
making_charge = 290  # Fixed making charge per gram
IST = pytz.timezone("Asia/Kolkata")

# ----------------------------
# Functions
# ----------------------------
def calculate_retail_price(gold_price_inr_per_gram):
    """Apply GST + fixed making charge."""
    gst = gold_price_inr_per_gram * 0.03
    final_price = gold_price_inr_per_gram + gst + making_charge
    return final_price

def get_gold_price_inr(gold_purity):
    """Fetch gold rate in INR/gram for 22k/24k purity."""
    gold_ticker = yf.Ticker("GC=F")
    usd_inr_ticker = yf.Ticker("USDINR=X")

    gold_data = gold_ticker.history(period="1d")
    inr_data = usd_inr_ticker.history(period="1d")

    if gold_data.empty or inr_data.empty:
        return None

    gold_price_usd = gold_data["Close"].iloc[-1]  # per troy ounce
    usd_inr = inr_data["Close"].iloc[-1]

    # Convert price per ounce to per gram INR (24k)
    gold_price_24k_inr_per_gram = (gold_price_usd * usd_inr) / 31.1035

    # Adjust for purity
    if gold_purity == "22k":
        multiplier = 22 / 24
    else:
        multiplier = 1  # 24k

    gold_price_inr_per_gram = gold_price_24k_inr_per_gram * multiplier

    # Final retail price with fixed making charge
    retail_price = calculate_retail_price(gold_price_inr_per_gram)
    return retail_price

def show_notification(title, message):
    """Show desktop popup notification."""
    try:
        notification.notify(title=title, message=message, timeout=10)
    except Exception as e:
        print("Notification error:", e)

def send_email(subject, body, receivers):
    """Send email using Gmail SMTP."""
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
def gold_rate_app():
    st.write("Enter your city, gold purity, and duration. The app will update every 60 seconds until time ends.")

    city = st.text_input("City name", value="")

    gold_purity = st.radio("Select Gold Purity", ["22k", "24k"], index=0)

    duration_minutes = st.number_input("Duration (minutes)", min_value=1, max_value=1440, value=1)

    receiver_email_input = st.text_input("Your Email", value="")

    email_possible = bool(SENDER_EMAIL and APP_PASSWORD)
    popup_opt = st.checkbox(
        "Show desktop popup notifications (every 1 min)", 
        value=False,
        help="A desktop popup notification will appear (every 60 sec) until the session ends."
    )
    send_email_opt = st.checkbox(
        "Send final gold rate via email",
        value=False,
        disabled=not email_possible,
        help="A mail including the final gold rate will be sent after the session ends."
    )

    if st.button("Start Monitoring"):
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        placeholder = st.empty()

        final_price = None
        final_time = None

        while datetime.now() < end_time:
            try:
                price = get_gold_price_inr(gold_purity)
                now_ist = datetime.now(IST).strftime("%I:%M %p, %d %b %Y")

                if price is not None:
                    final_price = price
                    final_time = now_ist

                    msg = (
                        f"Gold price {gold_purity} (INR/gm): {price:.2f}\n"
                        f"As of {now_ist} IST in {city}"
                    )

                    # Update the Streamlit UI
                    with placeholder.container():
                        st.success(f"🪙 Gold Rate in {city} ({gold_purity}) on **{now_ist}**: ***₹{price:.2f}/gm***")
                        st.write(f"Next update in 60 sec. Monitoring until **{end_time.strftime('%I:%M %p')}**.")

                    # Show popup if selected
                    if popup_opt:
                        show_notification(f"Gold Price in {city}", msg)

                else:
                    st.error("⚠️ Failed to fetch gold price.")

            except Exception as e:
                st.error(f"⚠️ Error: {e}")

            time_module.sleep(60)  # wait 1 minute

        # When monitoring ends
        with placeholder.container():
            st.warning(f"⏳ Time is **{end_time.strftime('%I:%M %p')}**. Your monitoring session ended!")

        # Send email only once at the end
        if send_email_opt and final_price is not None and receiver_email_input.strip():
            ok = send_email(
                subject="Final Gold Rate Report",
                body=(
                    f"City: {city}\n"
                    f"Date & Time: {final_time}\n"
                    f"Gold Purity: {gold_purity}\n"
                    f"Final Gold Price: ₹{final_price:.2f}/gm"
                ),
                receivers=[receiver_email_input.strip()],
            )

            if ok:
                st.success(f"📧 Final email sent to {receiver_email_input.strip()}!")
            else:
                st.error("❌ Could not send email. Check credentials.")
