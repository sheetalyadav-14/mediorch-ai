import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-pro")

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

def main_agent(user_message):
    try:
        response = model.generate_content(user_message)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"


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