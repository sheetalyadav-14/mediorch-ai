import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash-latest")

from fastapi import FastAPI
from pydantic import BaseModel
from google.cloud import firestore

db = firestore.Client()
app = FastAPI()

# ------------------ INPUT MODEL ------------------
class Query(BaseModel):
    user_id: str
    message: str


# ------------------ AGENTS ------------------

# 🧠 Health Agent
def health_agent(message):
    if "fever" in message:
        return "You may have mild fever. Stay hydrated and take rest."
    if "cold" in message:
        return "It looks like a common cold. Drink warm fluids."
    return None


# 💉 Vaccine Agent
def vaccine_agent(message):
    if "vaccine" in message:
        return "Your next vaccine is on 12 April."
    return None


# 🤖 General Agent
def general_agent(message):
    return "Please ask something related to health."


# ------------------ MAIN AGENT ------------------

def symptom_agent(message):
    prompt = f"""
    Analyze these symptoms: {message}.
    Explain in simple language.
    Possible causes only (no diagnosis).
    """
    response = model.generate_content(prompt)
    return response.text if hasattr(response, "text") else str(response)


def advice_agent(message):
    prompt = f"""
    Give basic health advice for: {message}.
    Keep it simple and safe.
    Do not prescribe medicines.
    """
    response = model.generate_content(prompt)
    return response.text if hasattr(response, "text") else str(response)


def risk_agent(message):
    prompt = f"""
    Check risk level for: {message}.
    Answer ONLY one word:
    LOW or MEDIUM or HIGH
    """
    response = model.generate_content(prompt)
    return response.text if hasattr(response, "text") else str(response)


def main_agent(message):
    try:
        symptom = symptom_agent(message)
        advice = advice_agent(message)
        risk = risk_agent(message)

        return f"""
Analysis:
{symptom}

Advice:
{advice}

Risk Level:
{risk}
"""

    except Exception as e:
        return str(e)


# ------------------ API ------------------

@app.get("/")
def home():
    return {"message": "MediOrch AI is running"}


@app.post("/chat")
def chat(query: Query):
    try:
        response = main_agent(query.message)

        db.collection("users").document(query.user_id).collection("history").add({
            "message": query.message,
            "response": response
        })

        return {"response": response}

    except Exception as e:
        return {"error": str(e)}

# ------------------ RUN ------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080)