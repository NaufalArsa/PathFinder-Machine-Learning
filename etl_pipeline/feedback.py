import json
import re
import requests
import os
from dotenv import load_dotenv
from flask import jsonify, make_response

load_dotenv()

# OpenRouter API configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = "deepseek/deepseek-r1-0528:free"
OPENROUTER_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

def strip_json_wrappers(text):
    """Cleans LLM response from code fences or markdown artifacts."""
    return re.sub(r"^.*?({.*?})\s*```?$", r"\1", text.strip(), flags=re.DOTALL)


def feedback(df):
    experience = df.get("Experience")
    skills     = df.get("skill")
    ability    = df.get("ability")
    program    = df.get("program")

    if not all([experience, skills, ability, program]):
        return make_response(jsonify(error="Missing required parameters"), 400)

    # Prompt format
    prompt = (
        f"Based on the following resume profile, write a professional technical CV review.\n\n"
        f"Experiences: {experience}\n"
        f"Skills: {skills}\n"
        f"Abilities: {ability}\n"
        f"Education: {program}\n\n"
        f"Return response as valid JSON formatted markdown with fields: strengths, weaknesses, and suggestions."
    )

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "CVReviewApp"
    }

    body = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(OPENROUTER_ENDPOINT, headers=headers, json=body)
        response.raise_for_status()
        result_text = response.json()["choices"][0]["message"]["content"]

        # Strip code blocks and markdown artifacts
        cleaned = re.sub(r"^(```json|```)", "", result_text.strip(), flags=re.IGNORECASE)
        cleaned = re.sub(r"```$", "", cleaned.strip())

        # Remove markdown formatting like **bold** or _italic_
        cleaned = re.sub(r"\*\*(.*?)\*\*", r"\1", cleaned)
        cleaned = re.sub(r"\*(.*?)\*", r"\1", cleaned)
        cleaned = re.sub(r"_(.*?)_", r"\1", cleaned)


        # Try parsing cleaned JSON
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            # Try one more time with alternate wrapper stripper
            cleaned = strip_json_wrappers(result_text)
            parsed = json.loads(cleaned)

        return make_response(jsonify(review=parsed), 200)

    except requests.exceptions.RequestException as e:
        return make_response(jsonify(error=f"HTTP request failed: {e}"), 502)
    except json.JSONDecodeError:
        return make_response(jsonify(error="Model responded with invalid JSON", raw=result_text), 500)
    except Exception as e:
        return make_response(jsonify(error=f"Review process failed: {e}"), 500)