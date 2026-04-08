from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Query(BaseModel):
    user_id: str
    message: str

@app.get("/")
def home():
    return {"message": "MediOrch AI is running"}

@app.post("/chat")
def chat(query: Query):
    user_msg = query.message.lower()

    response = []

    if "fever" in user_msg or "bukhar" in user_msg:
        response.append("You may have mild fever. Please take rest.")

    if "vaccine" in user_msg:
        response.append("Your next vaccine is on 12 April.")

    if not response:
        return {"response": "Please ask something related to health."}

    return {"response": " | ".join(response)}

    if __name__ == "__main__":
        import uvicorn
        uvicorn.run("main:app", host="0.0.0.0", port=8080)