# Resume Analysis & Job Recommendation API

This project provides an end-to-end ETL pipeline and Flask API for analyzing resumes, extracting key features, and recommending jobs using AI. The main job recommendation engine uses **cosine similarity** with TF-IDF vectorization, while an **LSTM model** is included for experimentation and learning purposes.

## Features

- **Resume Parsing:** Extracts skills, experience, education, and abilities from PDF resumes.
- **Job Recommendation:** Suggests the most relevant job titles based on resume content using cosine similarity (TF-IDF).
- **CV Review:** Generates a professional, AI-powered review of the resume, highlighting strengths, weaknesses, and suggestions.
- **LSTM Model (Experimental):** An LSTM-based model is included for research and learning, but is not used in production recommendations.
- **REST API:** Easy-to-use endpoints for integration with other systems or frontends.

## Project Structure

```
.
├── main.py                  # Flask API entry point
├── etl_pipeline/            # ETL and ML logic
│   ├── extract.py
│   ├── predict.py
│   ├── feedback.py
│   └── etl.txt
├── lstm/                    # LSTM model (experimental)
│   ├── app.py
├── dataset/                 # Sample datasets and reference data
├── models/                  # Pre-trained ML models
├── uploads/                 # Temporary storage for uploaded resumes
├── requirements.txt         # Python dependencies
└── README.md
```

## Quickstart: How to Run

1. **Install Python Requirements**
    ```sh
    pip install -r requirements.txt
    ```

2. **Download the English Model for spaCy**
    ```sh
    python -m spacy download en_core_web_sm
    ```

3. **Run the Flask API**
    ```sh
    python main.py
    ```

The API will be available at [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

## API Endpoints

### `/process-resume` (POST)

**Description:** Upload a PDF resume to receive a job recommendation.

**Request Example:**

- Content-Type: `multipart/form-data`
- Body:  
  - `file`: (attach your `cv.pdf`)

**Response Example:**

```json
{
    "cv_index": 1,
    "recommended_job_title": "Python/Data Visualization Developer, Internship",
    "similarity_score": "67.12%"
}
```

---

### `/review` (POST)

**Description:** Upload a PDF resume to receive an AI-generated CV review.

**Request Example:**

- Content-Type: `multipart/form-data`
- Body:  
  - `file`: (attach your `cv.pdf`)

**Response Example:**

```json
"review": {
    "strengths": [
        "Diverse technical exposure: Combines UX/UI design skills (Miro, Adobe, Photoshop) with backend development knowledge (Laravel, Database Systems)",
        "Relevant academic foundation: Coursework in UX Design, Database Systems, Programming, and Data Analytics aligns with technical roles"
    ],
    "suggestions": [
        "Resolve timeline conflicts: Clarify dates for overlapping roles (e.g., part-time vs. full-time) and remove duplicate entries",
        "Expand technical projects: Showcase portfolio pieces demonstrating Laravel/database implementations and UX solutions"
    ],
    "weaknesses": [
        "Conflicting/overlapping timelines: UI/UX Intern and Data Management Intern both listed for Feb-May 2025 creates chronological ambiguity",
        "Vague skill descriptions: Terms like 'system', 'management', and 'framework' lack context and specificity"
    ]
}
```

---

## Model Notes

- **Cosine Similarity (TF-IDF):** Used as the main method for job recommendation due to its effectiveness and interpretability.
- **LSTM Model:** Included for learning and experimentation. Not used in the main API workflow, but can be explored in `LSTM` folder.

---

## Python Version

- Recommended: **Python 3.10.18**

---

## License

MIT License

---

## Acknowledgements

- [spaCy](https://spacy.io/)
- [Flask](https://flask.palletsprojects.com/)
- [OpenRouter](https://openrouter.ai/)
