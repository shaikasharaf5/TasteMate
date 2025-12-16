from dotenv import load_dotenv


from flask import Flask, render_template, request
import google.generativeai as genai
import json
import re
import os

# Load environment variables
load_dotenv()

# Read API key safely
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")

app = Flask(__name__)

# =========================
# Helper: Safe JSON Extractor
# =========================
def extract_json(text):
    """
    Extracts the first valid JSON object from Gemini output.
    Prevents crashes due to extra text.
    """
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
        # Gemini Prompt
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

        Generate personalized recommendations.

        IMPORTANT:
        - Respond ONLY in valid JSON
        - No explanations
        - No markdown
        - No extra text

        JSON format:
        {{
          "breakfast": ["item1", "item2", "item3"],
          "dinner": ["item1", "item2", "item3"],
          "workouts": ["item1", "item2", "item3"]
        }}
        """

        # -------------------------
        # Gemini Call
        # -------------------------
        response = model.generate_content(prompt)
        # Debug (optional – comment after testing)
        print("RAW GEMINI OUTPUT:\n", response.text)

        # -------------------------
        # Parse Gemini Output Safely
        # -------------------------
        data = extract_json(response.text)

        # -------------------------
        # Render Results
        # -------------------------
        return render_template(
            'result.html',
            breakfast_names=data["breakfast"],
            dinner_names=data["dinner"],
            workout_names=data["workouts"],
            restaurant_names=[]
        )

    except Exception as e:
        # Safe fallback (never crash app)
        return render_template(
            'result.html',
            breakfast_names=["Oats", "Fruit Bowl", "Boiled Eggs"],
            dinner_names=["Rice & Dal", "Vegetable Curry", "Salad"],
            workout_names=["Walking", "Yoga", "Stretching"],
            restaurant_names=[]
        )


# =========================
# App Runner
# =========================
if __name__ == '__main__':
    app.run(debug=True)
