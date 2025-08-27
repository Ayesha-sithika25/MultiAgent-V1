# Gold Rate Notifier

A simple Python script that fetches the live gold price for a given city and displays it as a desktop notification.  
It uses Yahoo Finance for gold price data and updates every few seconds/minutes as configured. 
Perfect for tracking rates in real time!. 
Python version "3.13.6" is used to build this project.

# Features

- Fetches live gold price in INR per gram from Yahoo Finance.
- Supports 22k and 24k gold purity.
- Adds city-specific making charges.
- Calculates GST automatically.
- Displays desktop notifications with current rate.
- Configurable update interval.

# Installation

1. Install dependencies:

**pip install -r requirements.txt**

2. Run the script:

**python main.py**


# Usage 

1. City → Can be chnaged before running ("Chennai", or "Puducherry")

2. Gold_purity → You can choose to view with gold rate for respective city ("22k" or "24k")

3. Time → Can be changed to view result on certain time intervals. (30 mins or 24 hours)


# Notes

- Gold rates are based on Yahoo Finance live data.
- Making charges may vary per jeweler. Modify them in the city_making_charges dictionary.


👩‍💻 Author
Built by Ayesha as a demo project using open tools and Libraries.
