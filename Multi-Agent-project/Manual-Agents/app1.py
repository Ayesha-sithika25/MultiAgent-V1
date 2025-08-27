import streamlit as st

# Import agent apps
from Agents.air_quality import air_quality_app
from Agents.gold_rate import gold_rate_app
from Agents.nutrition import nutrition_app

# -------------------------
# Main Hub App
# -------------------------
st.set_page_config(page_title="AI Agents Hub", page_icon="🤖")

st.sidebar.title("🤖 AI Agents Hub")
choice = st.sidebar.radio(
    "Choose an Agent:",
    ["Air Quality Agent", "Gold Rate Agent", "Nutrition Agent"]
)

if choice == "Air Quality Agent":
    st.title("🌫️😷 Air Quality Agent")
    air_quality_app()

elif choice == "Gold Rate Agent":
    st.title("💰 Gold Rate Agent 🪙")
    gold_rate_app()

elif choice == "Nutrition Agent":
    st.title("🍎🥦 Nutrition Agent")
    nutrition_app()
