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
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("No JSON found in Gemini response")
    return json.loads(match.group())


# =========================
# Routes
# =========================
@app.route("/")
def index():
    return render_template("details.html")


@app.route("/recommend", methods=["POST"])
def recommend():
    try:
        # -------------------------
        # User Inputs
        # -------------------------
        age = request.form["age"]
        gender = request.form["gender"]
        weight = request.form["weight"]
        height = request.form["height"]
        veg_or_nonveg = request.form["veg_or_nonveg"]
        disease = request.form["disease"]
        region = request.form["region"]
        allergies = request.form["allergies"]
        foodtype = request.form["foodtype"]

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
            - Food quantities must be realistic for one person
            - Calories and macros must be nutritionally valid

            Respond ONLY in valid JSON in this exact format:
            for each meal and workout, provide 3+ options.
            {{
            "yoga":[
                {{
                "name": "Yoga Pose name",
                "duration": "e.g., 15 minutes",
                "calories_burned": "number in kcal"
                }}
            ],
            "breakfast": [
                {{
                "name": "Food name",
                "quantity": "e.g., 2 slices / 150g / 1 bowl",
                "calories": "number in kcal",
                "protein": "number in g",
                "carbs": "number in g",
                "fats": "number in g"
                }}
            ],
            "lunch": [
                {{
                "name": "Food name",
                "quantity": "e.g., 1 plate / 200g",
                "calories": "number in kcal",
                "protein": "number in g",
                "carbs": "number in g",
                "fats": "number in g"
                }}
            ],
            "dinner": [
                {{
                "name": "Food name",
                "quantity": "e.g., 2 chapatis / 1 cup",
                "calories": "number in kcal",
                "protein": "number in g",
                "carbs": "number in g",
                "fats": "number in g"
                }}
            ],
            "workouts": [
                {{
                "name": "Exercise name",
                "duration": "e.g., 20 minutes",
                "calories_burned": "number in kcal"
                }}
            ]
            }}
        """

        response = model.generate_content(prompt)
        # print("RAW GEMINI OUTPUT:\n", response.text)

        data = extract_json(response.text)

        # -------------------------
        # Store results in session
        # -------------------------
        session["results"] = data

        return redirect(url_for("results"))

    except Exception as e:
        print("ERROR:", e)

        session["results"] = {
            "yoga": [
                {
                    "name": "Sun Salutation",
                    "duration": "15 minutes",
                    "calories_burned": "100",
                }
            ],
            "breakfast": [
                {
                    "name": "Oats Porridge",
                    "quantity": "1 bowl",
                    "calories": "180",
                    "protein": "6",
                    "carbs": "30",
                    "fats": "4",
                },
                {
                    "name": "Boiled Eggs",
                    "quantity": "2 eggs",
                    "calories": "140",
                    "protein": "12",
                    "carbs": "2",
                    "fats": "10",
                },
                {
                    "name": "Fruit Bowl",
                    "quantity": "1 cup",
                    "calories": "120",
                    "protein": "2",
                    "carbs": "28",
                    "fats": "1",
                },
            ],
            "lunch": [
                {
                    "name": "Veg Salad",
                    "quantity": "1 bowl",
                    "calories": "100",
                    "protein": "3",
                    "carbs": "15",
                    "fats": "2",
                },
                {
                    "name": "rice with curry",
                    "quantity": "1 plate",
                    "calories": "350",
                    "protein": "10",
                    "carbs": "60",
                    "fats": "8",
                },
                {
                    "name": "roti with sabzi",
                    "quantity": "2 rotis",
                    "calories": "250",
                    "protein": "6",
                    "carbs": "40",
                    "fats": "5",
                },
            ],
            "dinner": [
                {
                    "name": "Steamed Rice",
                    "quantity": "1 cup",
                    "calories": "200",
                    "protein": "4",
                    "carbs": "45",
                    "fats": "1",
                },
                {
                    "name": "Dal",
                    "quantity": "1 bowl",
                    "calories": "150",
                    "protein": "10",
                    "carbs": "20",
                    "fats": "3",
                },
                {
                    "name": "Vegetable Curry",
                    "quantity": "1 bowl",
                    "calories": "120",
                    "protein": "4",
                    "carbs": "15",
                    "fats": "5",
                },
            ],
            "workouts": [
                {
                    "name": "Brisk Walking",
                    "duration": "30 minutes",
                    "calories_burned": "150",
                },
                {
                    "name": "Stretching",
                    "duration": "15 minutes",
                    "calories_burned": "50",
                },
                {"name": "Yoga", "duration": "20 minutes", "calories_burned": "80"},
            ],
        }

        return redirect(url_for("results"))


@app.route("/results")
def results():
    data = session.get("results")
    if not data:
        return redirect(url_for("index"))

    return render_template(
        "result.html",
        yoga=data["yoga"],
        breakfast=data["breakfast"],
        lunch=data["lunch"],
        workouts=data["workouts"],
        dinner=data["dinner"],
    )


# =========================
# App Runner
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
