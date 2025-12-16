from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session
import google.generativeai as genai
import json
import re
import os

# =========================
# Setup
# =========================
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")  # required for session


# =========================
# Helper: Safe JSON Extractor
# =========================
def extract_json(text):
    match = re.search(r'\{[\s\S]*\}', text)
    if not match:
        raise ValueError("No JSON found in Gemini response")
    return json.loads(match.group())


# =========================
# Routes
# =========================
@app.route('/')
def index():
    return render_template('details.html')


@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        # -------------------------
        # User Inputs
        # -------------------------
        age = request.form['age']
        gender = request.form['gender']
        weight = request.form['weight']
        height = request.form['height']
        veg_or_nonveg = request.form['veg_or_nonveg']
        disease = request.form['disease']
        region = request.form['region']
        allergies = request.form['allergies']
        foodtype = request.form['foodtype']

        # -------------------------
        # Prompt
        # -------------------------
        prompt = f"""
        You are a certified nutritionist and fitness coach.

        User Profile:
        - Age: {age}
        - Gender: {gender}
        - Weight: {weight} kg
        - Height: {height} cm
        - Diet preference: {veg_or_nonveg}
        - Health condition: {disease}
        - Allergies: {allergies}
        - Region: {region}
        - Preferred food type: {foodtype}

        STRICT RULES:
        - Do NOT include allergic foods
        - Prefer regional foods if possible
        - Respect diet preference strictly

        Respond ONLY in valid JSON:
        {{
          "breakfast": ["item1", "item2", "item3"],
          "dinner": ["item1", "item2", "item3"],
          "workouts": ["item1", "item2", "item3"]
        }}
        """

        response = model.generate_content(prompt)
        print("RAW GEMINI OUTPUT:\n", response.text)

        data = extract_json(response.text)

        # -------------------------
        # Store results in session
        # -------------------------
        session["results"] = data

        return redirect(url_for("results"))

    except Exception as e:
        print("ERROR:", e)

        session["results"] = {
            "breakfast": ["Oats", "Fruit Bowl", "Boiled Eggs"],
            "dinner": ["Rice & Dal", "Vegetable Curry", "Salad"],
            "workouts": ["Walking", "Yoga", "Stretching"]
        }
        return redirect(url_for("results"))


@app.route('/results')
def results():
    data = session.get("results")

    if not data:
        return redirect(url_for("index"))

    return render_template(
        'result.html',
        breakfast_names=data["breakfast"],
        dinner_names=data["dinner"],
        workout_names=data["workouts"]
    )


# =========================
# App Runner
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
