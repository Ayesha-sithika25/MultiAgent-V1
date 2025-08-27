# Project : Air-Quality-Agent

A Streamlit-based app that monitors PM2.5 air quality levels for a chosen city.  
It gives rule-based health suggestions, and can optionally send the final report via email.  
It is built using python version "3.13.6".

##  Features

- Get live PM2.5 air quality data for any city.
- Provides health-based suggestions from rule-based suggestions using WHO guidelines.
- Duration-based monitoring (1 minute to 24 hours), also be changable in code.
- Optional email report at the end of monitoring.
- Simple web interface built with Streamlit.

## Tech Stack

- [Streamlit](https://streamlit.io/) — Web app framework.
- [Open-Meteo API](https://open-meteo.com/) — Air quality data source.
- [Geopy](https://geopy.readthedocs.io/) — Geocoding for city -> latitude/longitude.
- [dotenv](https://pypi.org/project/python-dotenv/) — Secures email credentials.
- SMTP (Gmail) — Email sending.

## How to run

- Install dependencies:

*pip install -r requirements.txt*

- Set up environment variables in .env:

*SENDER_EMAIL=your_email@gmail.com*  
*APP_PASSWORD=your_app_password*

(For Gmail, create an App Password in your Google account settings.)

- Run the app by 

*streamlit run app.py* # To run streamlit project  
*python main.py* # To run simple project

## External page

- Enter City Name.
- Set Monitoring Duration (in minutes).
- Enter Your Email (optional, for report).
- Click Start Monitoring.

## Workflow

1. User Input - City name, duration, optional email.
2. Geocoding - Converts city into latitude and longitude.
3. Data Fetching - Call Open-Meteo API for PM2.5 data.
4. Suggestion Engine - Gives rule-based health messages based on value.
5. Live Updates - updates PM2.5 value and suggestion in UI every minute until the duration ends.
6. Final Step - Send email with latest result (if enabled).

## Example Output

> PM2.5 in Chennai on 02:15 PM, 14 Aug 2025: 18 µg/m³
> 
> Suggestion: Air quality is moderate. Sensitive groups should limit outdoor exertion.
> 
> Next update in 5 minutes. Monitoring until 03:15 PM.

Email (if enabled):

> Subject: Final Air Quality Report

> City: Chennai
> 
> Date & Time: 02:15 PM, 14 Aug 2025
> 
> Final PM2.5: 18 µg/m³
> 
> Suggestion: Air quality is moderate. Sensitive groups should limit outdoor exertion.

---

# Project : 'AQ-UI-with-Mail' and 'Air-Quality-Notifier'

This projects are Python script (Python version : 3.13.6) that runs in the background, fetching PM2.5 levels for a city and provides alerts. It shows results in the terminal, displays notifications, and sends email at regular intervals. Then they are integrated to a full interactive web application using Streamlit. 

## Sample Output

> 🟢 Air Quality Report
> 
> PM2.5: 65 µg/m³ in city Delhi
> 
> Suggestion: Moderate air quality. Safe but sensitive people should wear a mask.

> 📧 Email sent successfully.
> 
> ⏰ Waiting 300 seconds...

## Requirements for all 

streamlit  
requests  
geopy  
python-dotenv
plyer
pytz

---

## Progress

Old Project : Focused on background notifications and email alerts.

New Project : Introduced web-based UI, live updates, and optional reporting.
