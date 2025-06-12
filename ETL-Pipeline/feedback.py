import openai
import re
import json

openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

def feedback(df_row):
    experience = df_row['Experience']
    skills = df_row['skill']
    ability = df_row['ability']
    program = df_row['program']

    prompt = (
        f"Based on the following profile, give a professional technical review:\n\n"
        f"Experiences: {experience}\n"
        f"Skills: {skills}\n"
        f"Abilities: {ability}\n"
        f"Education: {program}\n\n"
        f"Format the response in clean markdown. Respond in structured JSON format with categories like: strengths, weaknesses, suggestions."
    )

    try:
        completion = openai.ChatCompletion.create(
            model="deepseek/deepseek-r1-0528:free",
            messages=[{"role": "user", "content": prompt}],
            extra_headers={  # <- header harus di sini
                "HTTP-Referer": "http://localhost",
                "X-Title": "CVReviewApp"
            }
        )
        review_result = completion.choices[0].message["content"]
        cleaned_review = re.sub(r"```json|```", "", review_result).strip()
        return json.loads(cleaned_review)
    except Exception as e:
        return {"error": f"LLM feedback error: {e}"}
