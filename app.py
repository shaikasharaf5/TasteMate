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

# Load fallback data once at startup for better performance
FALLBACK_DATA_PATH = os.path.join(os.path.dirname(__file__), "fallback_data.json")
with open(FALLBACK_DATA_PATH, "r") as f:
    FALLBACK_DATA = json.load(f)


# =========================
# Helper: Safe JSON Extractor
# =========================
def extract_json(text):
    # Use non-greedy match and more efficient regex pattern
    match = re.search(r"\{.*?\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON found in Gemini response")
    return json.loads(match.group())


# =========================
# Helper: Input Validator
# =========================
def validate_user_input(form_data):
    """Validate user inputs to prevent unnecessary API calls"""
    errors = []
    
    # Validate age
    try:
        age = int(form_data.get("age", 0))
        if age < 1 or age > 120:
            errors.append("Age must be between 1 and 120")
    except (ValueError, TypeError):
        errors.append("Invalid age")
    
    # Validate weight
    try:
        weight = float(form_data.get("weight", 0))
        if weight < 1 or weight > 500:
            errors.append("Weight must be between 1 and 500 kg")
    except (ValueError, TypeError):
        errors.append("Invalid weight")
    
    # Validate height
    try:
        height = float(form_data.get("height", 0))
        if height < 0.5 or height > 3.0:
            errors.append("Height must be between 0.5 and 3.0 meters")
    except (ValueError, TypeError):
        errors.append("Invalid height")
    
    return errors


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
        # Validate Inputs
        # -------------------------
        validation_errors = validate_user_input(request.form)
        if validation_errors:
            print("Validation errors:", validation_errors)
            # Use fallback data for invalid inputs
            session["results"] = FALLBACK_DATA
            return redirect(url_for("results"))

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
        # Use fallback data loaded at startup
        session["results"] = FALLBACK_DATA
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
