# Project : Nutrition-Agent

A Streamlit web app built using Python version 3.13.6.  
It retrieves nutrient information (Energy, Protein, Fat) for multiple foods and quantities.  
It uses the USDA FoodData Central API and can optionally send the results via email.

## Features

- Accepts multiple foods with grams (e.g., bread:100, egg:50, apple:30).
- Fetches nutrient information using USDA FDC API.
- Automatically scales nutrient values according to the given grams.
- Displays data in a clean Streamlit interface.
- Optionally sends results to an email address.

## Tech Stack

- [Streamlit](https://streamlit.io/) — Web interface  
- [USDA FoodData Central API](https://api.nal.usda.gov/fdc/v1/foods/search) — Nutrient data
- [dotenv](https://pypi.org/project/python-dotenv/) — Email credentials  
- requests - API calls
- SMTP (Gmail) — For sending email reports

## How to run

- Install dependencies:

*pip install -r requirements.txt*

- Set up environment variables in .env:

*SENDER_EMAIL=your_email@gmail.com*
*APP_PASSWORD=your_app_password*
*USDA_API_KEY=your_usda_api_key*

(For Gmail, create an App Password in your Google account settings.)

- Run the app:

*streamlit run app.py*

## External page

- Enter foods with grams, comma-separated: 
*bread:100, egg:50, apple:30*
- Check "Send results to email?" (optional).
- Enter recipient email if enabled.
- Click Get Nutrients.

## Workflow

1. User Input – Foods and grams (comma-separated).
2. API Call – USDA FDC API fetches best match for each food.
3. Nutrient Extraction – Energy, Protein, Fat are extracted and scaled to specified grams.
4. Display – Nutrients shown on Streamlit page.
5. Email (Optional) – Sends compiled results to the entered email address.

## Example Output

> WHEAT BREAD (100.0 g)
> 
> Energy: 267.0 kcal  Protein: 11.1 g  Fat: 2.22 g

> MILK (150.0 g)
> 
> Energy: 82.5 kcal  Protein: 5.085 g  Fat: 3.18 g

> CHICKEN (500.0 g)
> 
> Energy: 535.0 kcal  Protein: 107.0 g  Fat: 8.95 g

Email Output (if enabled):

> Subject: Nutrient Results

> Here are your nutrient results:

> CHICKEN BIRIYANI WITH BASMATI RICE (200.0 g)
> 
> Energy: 234.0 kcal  Protein: 16.48 g  Fat: 5.3 g

## Requirements

streamlit  
requests  
python-dotenv

