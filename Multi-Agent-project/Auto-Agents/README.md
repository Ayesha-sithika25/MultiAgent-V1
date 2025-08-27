# Auto-Agents

This project is a Stremalit-based AI hub built using Python (version 3.13.6) that intelligently routes user queries to different agents based on the query :
- Air Quality Agent - Check air quality and pollution levels.
- Gold Rate Agent – View current gold prices.
- Nutrition Agent – Get nutritional values for foods.

## Features

- Streamlit UI – Interactive dashboard and chat interface.
- Agentic System – AI-powered query routing.
- Session State – Maintains chat history and agent context.
- Fallback Mechanisms – Ensures routing even if AI models are not available.

## Tech Stack 

- [Streamlit](https://streamlit.io/) — Web interface  
- [USDA FoodData Central API](https://api.nal.usda.gov/fdc/v1/foods/search) — Nutrient data
- [dotenv](https://pypi.org/project/python-dotenv/) — Email credentials  
- requests - API calls
- Transformers (Hugging Face) – AI/NLP models:
  - `facebook/bart-large-mnli` for zero-shot classification.
  - `distilbert-base-uncased` as a fallback.
  - logging – For debugging and monitoring.
- SMTP (Gmail) — For sending email reports

## How to run

- Create and activate a virtual environment:

*python -m venv venv*  
*venv\Scripts\activate*  # Windows  

- Install dependencies:

*pip install -r requirements.txt*

- Set up environment variables in .env:

*SENDER_EMAIL=your_email@gmail.com*  
*APP_PASSWORD=your_app_password*  
*USDA_API_KEY=your_usda_api_key*  
*HUGGINGFACE_API_KEY=you=r_api_key*

(For Gmail, create an App Password in your Google account settings.)

- Run the app:

*streamlit run app.py*

It will automatically open UI page or Open http://localhost:8501 in your browser.

## Workflow

1. User Input – You ask a question (e.g., "What's the AQI in New York?").
2. Router Agent – AI classifier analyzes the query using:
   - Zero-Shot Classification with BART-large-MNLI (local model).
   - DistilBERT text classification (fallback if BART is unavailable).
   - Hugging Face API (if no local models are available).
   - Keyword Matching as a last fallback.
3. Agent Selection – Based on classification, routes to:
   - `air_quality` app
   - `gold_rate` app
   - `nutrition` app
4. Agent Response – Displays results in a Streamlit UI, with suggestions.
5. Manual Control – Sidebar allows you to select an agent manually.

## External page

- Enter query that you want to ask
- Enter inputs of what you want to find in respective opened agent.
- Get your results.

## Example Output

> **"How is air pollution today"**

> I'll help you with that using our gold rate agent.

> I can help you with:
>
> Current gold prices
> 
> Price trends analysis
>
> Get Email reports

Then it will route to the right agent, display it for you to give inputs.

## Requirements

geopy  
plyer  
python-dotenv  
pytz  
requests  
streamlit  
yfinance  
transformers  
torch  
sentence-transformers
