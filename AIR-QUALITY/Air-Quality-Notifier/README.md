Air Quality Notifier with Email and Popup Alert

This project monitors real-time air quality (PM2.5) in a city using Open-Meteo’s API, and sends email alerts along with local popup notifications every 5 minutes. It is built with Python version "3.13.6" and uses secure `.env` configuration for credentials.

Features : 

Fetches live PM2.5 data using Open-Meteo API
Sends email alerts with rule based safety suggestions
Displays popup notifications on desktop
Uses `.env` file to keep email credentials safe
Runs continuously with pre-defined intervals

How to Run : 

1. Install required packages

pip install -r requirements.txt

or manually install with like this,

pip install requests geopy plyer python-dotenv

2. Create .env file

Create a file named .env in project folder and add the following:

SENDER_EMAIL=sender@gmail.com
APP_PASSWORD=app_password
RECEIVER_EMAILS=receiver1@gmail.com,receiver2@gmail.com

Note : Provide original credentials in this file, it will be fetched by main file

3. Run the script

python main.py


🏙️ Default Settings

1. City can be changed inside the main file to get value from expected city.

City: Delhi or City: Puducherry

2. Interval time can be changed inside main file to get notifications on expected time interval.

 Interval: 300 (Every 5 minutes) or 30 (Every 30 seconds)


Sample Output :

🟢 Air Quality Report
PM2.5: 65 µg/m³ in city Delhi
Suggestion: Moderate air quality. Safe but sensitive people should wear a mask.
📧 Email sent successfully.
⏰ Waiting 300 seconds...


👩‍💻 Author
Built by Ayesha as a demo project using open tools and APIs.
