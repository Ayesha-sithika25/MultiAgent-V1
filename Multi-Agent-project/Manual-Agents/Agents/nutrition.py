import streamlit as st
import requests
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# -------------------------
# Load environment variables
# -------------------------
load_dotenv()
SENDER_EMAIL = os.getenv("SENDER_EMAIL")   # Your Gmail address
APP_PASSWORD = os.getenv("APP_PASSWORD")   # Your App Password
API_KEY = os.getenv("USDA_API_KEY")        # USDA API Key


# -------------------------
# Functions
# -------------------------
def get_food_nutrients(query, grams=100, api_key=API_KEY, page_size=50):
    """
    Search USDA FDC for `query`, pick best, return dict with Energy, Protein, Fat scaled to grams.
    """
    url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {"query": query, "pageSize": page_size, "api_key": api_key}
    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        return {"error": f"API error {resp.status_code}"}
    data = resp.json()
    foods = data.get("foods", [])
    if not foods:
        return {"error": f"No foods found for {query}"}

    # --- Scoring function ---
    def score_food(f):
        desc = (f.get("description", "") or "").lower()
        dtype = (f.get("dataType", "") or "").lower()
        score = 0
        if desc.strip() == query.lower():
            score += 10
        if any(w in desc for w in ("raw", "fresh", "uncooked", "with skin", "without skin", "peeled")):
            score += 6
        if dtype in ("foundation", "sr legacy", "survey foods"):
            score += 3
        if any(w in desc for w in ("dried", "powder", "chips", "flour", "cooked", "canned",
                                   "roasted", "fried", "baked", "sauce", "syrup", "juice", "bar")):
            score -= 8
        return score

    scored = sorted(((score_food(f), f) for f in foods), key=lambda x: x[0], reverse=True)
    _, food = scored[0]

    def find_nutrient(food, targets):
        for n in food.get("foodNutrients", []):
            name = (n.get("nutrientName") or "").lower()
            for t in targets:
                if t.lower() == name or t.lower() in name:
                    return n.get("value"), (n.get("unitName") or "").strip()
        return None, None

    energy_val, energy_unit = find_nutrient(food, ["Energy"])
    prot_val, prot_unit = find_nutrient(food, ["Protein"])
    fat_val, fat_unit = find_nutrient(food, ["Total lipid (fat)", "Fat"])

    # --- Scaling ---
    def scale_and_convert(value, unit, grams):
        if value is None:
            return None, None
        u = (unit or "").lower()
        if u in ("kj", "kilojoule", "kilojoules"):
            kcal = value / 4.184
            return round(kcal * grams / 100.0, 2), "kcal"
        if u in ("kcal", "kilocalorie", "calorie"):
            return round(value * grams / 100.0, 2), "kcal"
        if u in ("g", "gram", "grams"):
            return round(value * grams / 100.0, 3), "g"
        if u in ("mg", "milligram", "milligrams"):
            return round((value / 1000.0) * grams / 100.0, 4), "g"
        return round(value * grams / 100.0, 3), unit

    energy, energy_u = scale_and_convert(energy_val, energy_unit, grams)
    protein, prot_u = scale_and_convert(prot_val, prot_unit, grams)
    fat, fat_u = scale_and_convert(fat_val, fat_unit, grams)

    return {
        "food": food.get("description"),
        "grams": grams,
        "energy": f"{energy} {energy_u}" if energy else "N/A",
        "protein": f"{protein} {prot_u}" if protein else "N/A",
        "fat": f"{fat} {fat_u}" if fat else "N/A"
    }


def send_email(recipient, results):
    msg = EmailMessage()
    msg["Subject"] = "Nutrient Results"
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient

    body = "Here are your nutrient results:\n\n"
    for res in results:
        if "error" in res:
            body += res["error"] + "\n\n"
        else:
            body += (
                f"{res['food']} ({res['grams']} g)\n"
                f"Energy: {res['energy']}\n"
                f"Protein: {res['protein']}\n"
                f"Fat: {res['fat']}\n\n"
            )
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(SENDER_EMAIL, APP_PASSWORD)
        smtp.send_message(msg)


# -------------------------
# Streamlit App
# -------------------------
def nutrition_app():
    st.write("Enter multiple foods with grams. Example:\n`bread:100, egg:50, apple:30`")

    foods_input = st.text_input("Foods and grams (comma-separated)", value="")
    send_email_check = st.checkbox("Send results to email?")
    email_input = st.text_input("Enter recipient email (if checked)")

    if st.button("Get Nutrients"):
        results = []
        food_items = [f.strip() for f in foods_input.split(",") if f.strip()]
        for item in food_items:
            if ":" in item:
                food, g = item.split(":")
                try:
                    grams = float(g.strip())
                except:
                    grams = 100
                res = get_food_nutrients(food.strip(), grams)
                results.append(res)
            else:
                results.append({"error": f"Invalid format for {item}"})

        for res in results:
            if "error" in res:
                st.error(res["error"])
            else:
                st.subheader(f"{res['food']} ({res['grams']} g)")
                st.write(f"**Energy:** {res['energy']}")
                st.write(f"**Protein:** {res['protein']}")
                st.write(f"**Fat:** {res['fat']}")

        if send_email_check and email_input.strip():
            try:
                send_email(email_input.strip(), results)
                st.success(f"Results sent to {email_input}")
            except Exception as e:
                st.error(f"Email sending failed: {e}")
