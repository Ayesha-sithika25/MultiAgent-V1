# Gold Rate Widget

Developed a  lightweight, transparent, always-on-top desktop widget using GUI(Tkinter) and python verison "3.13.6".
It shows the live gold price (INR per gram) for your city with changable gold purity and making charges.

# Features

- Displays live gold price in a small, movable, and resizable GUI window.
- Supports both *22k* and *24k* gold purity.
- Includes city-specific making charges and GST calculation for final retail price.
- Converts fetched price(USD) into (INR) by fetching exchange rates.
- Set making charges 300 by default if given city not found.
- Updates price automatically at specific intervals.
- Shows timestamp in IST timezone.
- Prints current price info in terminal as well.

# Installation

Intrall dependencies 

   **pip install yfinance pytz**

Run the script

   **pyhton main.py**

# Usage

1. City — Can be changed ("Chennai", "Trichy", "Cuddalore")

2. Gold purity — Can be changed between "22k" and "24k"

3. Updating time — update interval in seconds ("60" -> updates every minute)

# Widget working 

- The widget window will appear on the desktop.
- Drag the widget by left-clicking and moving.
- Resize by right-click dragging.

# Notes

1. Making charges are set per city; add or adjust in the city_making_charges dictionary.

2. The widget is transparent and stays on top of other windows for convenience.

3. Requires an active internet connection to fetch live data from Yahoo Finance.

