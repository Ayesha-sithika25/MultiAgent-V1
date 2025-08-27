# 💰 Gold Rate Agent with UI (Mail + Desktop Notification)

A Streamlit web app that monitors live gold prices (22k / 24k) for a chosen city.  
It shows updated price every minute and built using python version "3.13.6"..  
It can optionally send the final report via email or display desktop popup notifications or do the both when user checks.

# Features

- Fetches live gold price in INR/gram from Yahoo Finance.
- Supports both 22k and 24k purity.
- Adds GST + making charges automatically.
- Updates every 60 seconds until the session ends.
- Duration-based monitoring (1 minute to 24 hours), also be changable in code.
- optional desktop popup notification and email report with the final price.
  
# Tech Stack

- [Streamlit](https://streamlit.io/) — Web interface  
- [Yahoo Finance API](https://pypi.org/project/yfinance/) — Live gold & USD/INR data  
- [plyer](https://pypi.org/project/plyer/) — Desktop notifications  
- [dotenv](https://pypi.org/project/python-dotenv/) — Email credentials  
- SMTP (Gmail) — For sending email reports

# Installation

1. Install dependencies:

*pip install -r requirements.txt*

2. Set up environment variables in .env:

*SENDER_EMAIL=your_email@gmail.com*  
*APP_PASSWORD=your_app_password*

(For Gmail, create an App Password in your Google account settings.)

3. Run the app by 

*streamlit run app.py*

# External page

- Enter city name.
- Select 22k or 24k purity.
- Set duration (minutes).
- Enter Your Email (optional, for final report).
- Enable popup/email checkboxes (optional)
- Click Start Monitoring.

# Workflow

1. User Input - City name, purity, duration, optional email.
2. Fetch Data - Yahoo Finance (Gold & USD/INR).
3. Calculate Retail Price - Apply GST + making charges.
4. Live Updates - Updates gold price in UI every minute until the duration ends (and popups if enabled).
5. Final Step - Send email with latest result (if enabled).

# Example Output

> 🪙 Gold Rate in Chennai (22k) on 02:15 PM, 18 Aug 2025: ₹9479.29/gm  
> Next update in 60 sec. Monitoring until 02:45 PM.

Email (if enabled):

> Subject: Final Gold Rate Report

> City: puducherry  
> Date & Time: 05:46 PM, 18 Aug 2025  
> Gold Purity: 22k    
> Final Gold Price: ₹9284.08/gm


Desktop popup (if enabled):

> Gold Price in puducherry
> Gold price 22k (INR/gm): 9284.08
> As of 05:46 PM, 18 Aug 2025 IST in puducherry


After session ends:

> ⏳ Time is 05:47 PM. Your monitoring session ended!  
> Next update in 60 sec. Monitoring until 05:47 PM.
  
> 📧 Final email sent to **USER_EMAIL!


# Requirements

plyer==2.1.0  
python-dotenv==1.1.1  
pytz==2025.2  
streamlit==1.48.1  