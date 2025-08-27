import yfinance as yf
from datetime import datetime
import pytz
import sys
import tkinter as tk
from tkinter import Label

# -------------------
# Config
# -------------------
city = "Chennai"           # Change city here
gold_purity = "22k"        # Choose "22k" or "24k"
update_interval_sec = 60   # updates every minute

# Making charges per city (₹/gm)
city_making_charges = {
    "cuddalore": 350,
    "chennai": 400,
    "mumbai": 450,
    "delhi": 400,
    "kolkata": 380,
}

# -------------------
# Price Calculation
# -------------------
def calculate_retail_price(gold_price_inr_per_gram, making_charge=300):
    """Retail price = base gold price + making charge + GST (3%)"""
    gst = 0.03 * (gold_price_inr_per_gram + making_charge)  # 3% GST
    return gold_price_inr_per_gram + making_charge + gst

def get_gold_price_inr():
    """Fetch gold price in INR per gram with purity, making charges & GST"""
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
    else:
        multiplier = 1

    gold_price_inr_per_gram = gold_price_24k_inr_per_gram * multiplier

    # Get making charge for city (default 300 if city not found)
    making_charge = city_making_charges.get(city.lower(), 300)

    # Calculate retail price
    return round(calculate_retail_price(gold_price_inr_per_gram, making_charge), 2)

# -------------------
# Terminal Output
# -------------------
def print_terminal(price):
    tz = pytz.timezone("Asia/Kolkata")
    now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S IST")
    print(f"Python version: {sys.version.split()[0]}")
    print(f"Fetching gold price in {city}...")
    print(f"Gold price {gold_purity} (INR/gm): {price}")
    print(f"As of {now}\n")

# -------------------
# Movable & Resizable Widget
# -------------------
class GoldWidget:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)  # Remove window borders
        self.root.attributes("-topmost", True)  # Always on top
        self.root.attributes("-alpha", 0.85)  # Transparency

        self.label = Label(root, text="", font=("Segoe UI", 12), bg="#222", fg="white", padx=10, pady=5)
        self.label.pack(fill="both", expand=True)

        # Make draggable
        self.label.bind("<Button-1>", self.start_move)
        self.label.bind("<B1-Motion>", self.do_move)

        # Allow resize with bottom-right corner drag
        self.root.bind("<Button-3>", self.start_resize)
        self.root.bind("<B3-Motion>", self.do_resize)

        self.update_price()

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def start_resize(self, event):
        self._geom = (event.x_root, event.y_root, self.root.winfo_width(), self.root.winfo_height())

    def do_resize(self, event):
        dx = event.x_root - self._geom[0]
        dy = event.y_root - self._geom[1]
        new_width = max(150, self._geom[2] + dx)
        new_height = max(50, self._geom[3] + dy)
        self.root.geometry(f"{new_width}x{new_height}")

    def update_price(self):
        price = get_gold_price_inr()
        tz = pytz.timezone("Asia/Kolkata")
        now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S IST")

        if price:
            # Update widget text
            self.label.config(
                text=f"Live Gold Price in {city}\nGold price {gold_purity} (INR/gm): {price}\nAs of {now}"
            )

            # Only print to terminal now (no popup)
            print_terminal(price)

        # Schedule next update
        self.root.after(update_interval_sec * 1000, self.update_price)

# -------------------
# Run Widget
# -------------------
def run_widget():
    root = tk.Tk()
    app = GoldWidget(root)
    root.mainloop()

if __name__ == "__main__":
    run_widget()
