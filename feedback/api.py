# feedback_api.py
from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests

app = FastAPI()

OLLAMA_API_URL = "http://localhost:11434/api/generate"

class CVInput(BaseModel):
    cv_text: str

@app.post("/feedback")
def get_feedback(data: CVInput):
    prompt = f"""
    Anda adalah pakar HRD. Evaluasilah CV berikut dan berikan saran perbaikannya secara profesional:

    {data.cv_text}
    """

    response = requests.post(OLLAMA_API_URL, json={
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    })

    if response.status_code == 200:
        result = response.json()
        return {"feedback": result.get("response", "")}
    else:
        return {"error": "Gagal mengambil feedback dari Ollama"}, response.status_code
