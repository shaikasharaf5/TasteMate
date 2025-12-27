# AI-Based Food & Workout Recommendation System

This is a Flask-based web application that provides **personalized food and workout recommendations** using **Google Gemini AI**.  
Recommendations are generated based on user details such as age, gender, diet preference, health conditions, allergies, and region.

---

## 🚀 Features

- Personalized breakfast & dinner suggestions
- Workout recommendations
- Gemini AI integration
- Secure API key handling using `.env`
- Flask backend with HTML templates
- Robust JSON handling for AI responses

---

## 🛠 Tech Stack

- **Backend:** Python, Flask
- **AI:** Google Gemini API
- **Frontend:** HTML, CSS
- **Environment Management:** python-dotenv
- **Version Control:** Git & GitHub

---

## 📁 Project Structure
```
project/
│── app.py
│── requirements.txt
│── .env
│── .gitignore
│── README.md
│── templates/
│ ├── details.html
│ └── result.html
└── static/
```
---

## ⚙️ Prerequisites

- Python 3.9 or higher
- pip
- Git
- Gemini API key

---

## ▶️ How to Run the Project

1️⃣ Clone the repository
```
git clone https://github.com/shaikasharaf5/TasteMate.git
cd TasteMate
```

### 🔐 Environment Setup

#### Create a `.env` file (DO NOT COMMIT)

```
GEMINI_API_KEY=your_gemini_api_key_here
```
Make sure .env is listed in .gitignore.

📦 Install Dependencies
```
pip install -r requirements.txt
```
---
2️⃣ (Optional but recommended) Create virtual environment

Windows
```
python -m venv venv
venv\Scripts\activate
```

Linux / macOS
```
python3 -m venv venv
source venv/bin/activate
```
---
3️⃣ Run the Flask app
```
python app.py
```
---

4️⃣ Open in Browser
http://127.0.0.1:5000/

---

🧪 How It Works


- User fills the form with personal details

- Data is sent to Flask backend

- Gemini AI generates recommendations

- JSON response is safely parsed

- Results are displayed on UI
  


🔒 Security Notes

- Never hardcode API keys

- Never push .env to GitHub

- Rotate keys if accidentally exposed

- Use environment variables in production
  


📌 Future Enhancements

- Calorie & macro calculation

- User authentication

- Recommendation history

- Indian regional food optimization

- Database integration (MongoDB / PostgreSQL)

- MERN stack version

📜 License

-- This project is intended for educational and learning purposes.

