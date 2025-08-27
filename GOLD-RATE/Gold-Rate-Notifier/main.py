import yfinance as yf
from plyer import notification
from datetime import datetime
import time
import pytz
import sys

print("Python version:", sys.version)

# --- Config ---
city = "Chennai"          # Change city here
gold_purity = "22k"         # Choose "22k" or "24k"
update_interval_sec = 7200  # 2 hours once

# Making charges per city (₹ per gram)
city_making_charges = {
    "cuddalore": 350,
    "chennai": 400,
    "mumbai": 450,
    "delhi": 400,
    "kolkata": 380,
    # Add more cities as needed
}

def calculate_retail_price(gold_price_inr_per_gram, making_charge=300):
    gst = 0.03 * (gold_price_inr_per_gram + making_charge)  # 3% GST
    return gold_price_inr_per_gram + making_charge + gst

def get_gold_price_inr():
    gold_ticker = yf.Ticker("GC=F")
    usd_inr_ticker = yf.Ticker("USDINR=X")

    gold_data = gold_ticker.history(period="1d")
    inr_data = usd_inr_ticker.history(period="1d")

    if gold_data.empty or inr_data.empty:
        return None

    gold_price_usd = gold_data["Close"].iloc[-1]  # per troy ounce
    usd_inr = inr_data["Close"].iloc[-1]

    # Convert price per ounce to price per gram INR (24k)
    gold_price_24k_inr_per_gram = (gold_price_usd * usd_inr) / 31.1035

    # Adjust price based on purity
    if gold_purity == "22k":
        multiplier = 22 / 24
    elif gold_purity == "24k":
        multiplier = 1
    else:
        print("⚠️ Invalid gold purity selected, defaulting to 24k")
        multiplier = 1

    gold_price_inr_per_gram = gold_price_24k_inr_per_gram * multiplier

    # Get making charge for city (default 300 if city not found)
    making_charge = city_making_charges.get(city.lower(), 300)

    # Calculate retail price with making charge + GST
    retail_price = calculate_retail_price(gold_price_inr_per_gram, making_charge)

    return retail_price

def show_notification(title, message):
    notification.notify(title=title, message=message, timeout=10)

def main():
    ist = pytz.timezone('Asia/Kolkata')

    while True:
        print(f"Fetching gold price in {city}...")
        price = get_gold_price_inr()
        if price is not None:
            now_ist = datetime.now(ist)
            message = (
                f"Gold price {gold_purity} (INR/gm): {price:.2f}\n"
                f"As of {now_ist:%Y-%m-%d %H:%M:%S} IST"
            )
            print(message)
            show_notification(f"Live Gold Price in {city}", message)
        else:
            print("Failed to fetch gold price.")

        time.sleep(update_interval_sec)

if __name__ == "__main__":
    main()

# pip install yfinance plyer pytz