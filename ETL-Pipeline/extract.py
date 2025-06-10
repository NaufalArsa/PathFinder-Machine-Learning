import uuid
import re
from pathlib import Path
from typing import Union
import pdfplumber
import spacy
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from datetime import datetime
from dateutil import parser as dateparser

pytesseract.pytesseract.tesseract_cmd = r"D:\DBS\Capstone Project\Extract\Tesseract\tesseract.exe"

# Load NLP model with error handling
try:
    nlp = spacy.load("en_core_web_sm")
except Exception as e:
    print(f"Error loading Spacy NLP model: {e}")
    nlp = None

# Keywords for different resume sections
COMMON_SKILLS = {
    "python", "java", "c++", "c#", "go", "r", "scala", "sql", "mysql", "postgresql",
    "oracle", "mongodb", "excel", "html", "css", "javascript", "typescript",
    "pandas", "numpy", "scipy", "matplotlib", "seaborn", "sklearn", "tensorflow",
    "keras", "pytorch", "machine learning", "data visualization", "react",
    "django", "flask", "fastapi", "spring", "node.js", "git", "github", "docker",
    "aws", "azure", "gcp", "tableau", "photoshop", "figma", "canva", "jira",
    "notion", "airflow", "spark", "hadoop", "bigquery", "databricks", "English"
}

SKILL_KEYWORDS = ["skill", "skills", "technical skill", "programming language", "soft skills", "languages", "frameworks", "couserworks", "tools"]

EDUCATION_KEYWORDS = {"education", "degree", "university", "college", "coursework", "courses"}

EXPERIENCE_KEYWORDS = {"intern", "assistant", "manager", "developer", "engineer", 
                        "designer", "coordinator", "lead", "officer", "specialist",
                        "analyst", "consultant", "staff"}

ABILITY_KEYWORDS = [
    "developing", "creating", "building",
    "designing", "implementing", "making",
    "managing", "leading", "collaborating",
    "analyzing", "optimizing", "researching",
    "engineering", "automating", "testing",
    "planning", "mentoring", "preparing", "leading", 
    "brainstorming", "searching", "working"
]

DATE_PATTERN = r'([A-Za-z]{3,10})\s*(\d{4})'


def extract_text(path: Union[str, Path]) -> str:
    """Extract text dynamically based on file type."""
    path = Path(path)
    try:
        if path.suffix.lower() == ".pdf":
            return extract_text_from_pdf(path)
        elif path.suffix.lower() in [".png", ".jpg", ".jpeg", ".tiff"]:
            return extract_text_via_ocr(path)
        else:
            return ""
    except Exception as e:
        print(f"Error reading {path.name}: {e}")
        return ""


def extract_text_from_pdf(pdf_path: Union[str, Path]) -> str:
    """Extract text from a PDF using pdfplumber, fallback to OCR if necessary."""
    text = ""
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            text += extracted + "\n" if extracted else ""

    if not text.strip():
        return extract_text_via_ocr(pdf_path)
    return text


def extract_text_via_ocr(image_path: Union[str, Path]) -> str:
    """Extract text using OCR from scanned PDFs or images."""
    text = ""
    if image_path.suffix.lower() == ".pdf":
        images = convert_from_path(str(image_path))
        for img in images:
            text += pytesseract.image_to_string(img) + "\n"
    else:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)

    return clean_text(text)


def clean_text(text: str) -> str:
    """Cleans text by removing extra characters."""
    text = re.sub(r'(\\n|\\r|\\t|\n|\r|\t)+', '\n', text)
    # text = re.sub(r'[\▪️\-\|\[\]\●\+\•\.\:]', '', text)
    text = re.sub(r'[▪️\-\[\]●+•.:|\'%]', '', text)
    return text.strip()


def extract_name(lines):
    """Extracts name from resume header using NLP."""
    for line in lines[:5]:
        clean_line = line.strip()
        if clean_line and not any(char.isdigit() for char in clean_line):
            return clean_line

    doc = nlp("\n".join(lines[:5]))
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text.strip()

    return "Unknown"


def extract_skills(lines):
    skill_block = False
    extracted_skills = set()

    for line in lines:
        lower_line = line.lower()

        # Trigger extraction when any skill-related keyword is found
        if "skill" in lower_line or "skills" in lower_line or "technical skills" in lower_line or "programming language" in lower_line or "soft skills" in lower_line or "languages" in lower_line:
            skill_block = True
            continue

        # Stop extraction when encountering an empty line
        if skill_block and any(kw in lower_line for kw in ["experience", "certification", "project", "skills", "certificate"]):
            skill_block = False

                # Extract skills while inside the detected section
        if skill_block:
            extracted_skills.update(re.findall(r'\b[a-zA-Z0-9+#.]+\b', lower_line))

    # Ensure filtering remains intact
    filtered_skills = {skill.strip() for skill in extracted_skills if skill.lower() not in ["and"]}

    return filtered_skills


def extract_education(lines):
    """Extracts education details dynamically based on keywords and calculates duration."""
    education_entries = []
    edu_block = False
    start_year = None

    for line in lines:
        lower_line = line.lower().strip()

        # **Start extracting when any education keyword is found**
        if any(ek in lower_line for ek in EDUCATION_KEYWORDS):
            edu_block = True
            education_entries.append(line.strip())  # Store the first detected education header line
            continue
        
        # **Stop capturing when another major section header appears**
        if edu_block and any(kw in lower_line for kw in ["experience", "certification", "project", "skills", "projects"]):
            edu_block = False

        # **Capture education details**
        match = re.search(DATE_PATTERN, line)  # Look for years (e.g., 2019, 2022)
        if edu_block and match:
            if start_year is None:
                start_year = match.group(1)
            else:
                end_year = match.group(1)
                duration = calculate_months(f"Jan {start_year}", f"Dec {end_year}")
                education_entries.append(f"{line.strip()} [{duration} months]")
                start_year = None  # Reset for next entry

    return education_entries



def extract_experience(lines):
    """Extracts job titles and durations dynamically."""
    experience_entries = []

    for i in range(len(lines)):
        line = lines[i].strip()
        if any(role in line.lower() for role in EXPERIENCE_KEYWORDS):
            context = "\n".join(lines[i:i + 3])
            dates = re.findall(DATE_PATTERN, context, flags=re.IGNORECASE)

            if dates:
                start = f"{dates[0][0]} {dates[0][1]}"
                end = f"{dates[1][0]} {dates[1][1]}" if len(dates) > 1 else "Present"
                duration = calculate_months(start, end)
                role_title = line
                if duration >= 1:
                    experience_entries.append(f"{role_title} [{duration} months]")

    return experience_entries


def extract_ability(lines):
    """Extracts abilities from resume text based on action-oriented phrases."""
    try:
        ability_entries = []

        for line in lines:
            lower_line = line.lower().strip()

            if any(phrase in lower_line for phrase in ABILITY_KEYWORDS):
                ability_entries.append(line.strip())

        return ability_entries
    except Exception as e:
        print(f"Error extracting abilities: {e}")
        return []

def calculate_months(start: str, end: str) -> int:
    """Calculates months between two dates."""
    try:
        start_date = dateparser.parse(start)
        end_date = dateparser.parse(end) if end.lower() not in ["present", "now"] else datetime.today()
        return max(0, (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month))
    except:
        return 0


def extract_resume_features(filepath: Union[str, Path]) -> dict:
    """Master function to extract all structured details from a resume, including raw extracted text."""
    filepath = Path(filepath)
    raw_text = extract_text(filepath)  # Extract text from PDF or OCR
    text = clean_text(raw_text)
    lines = text.split("\n")

    return {
        "ID": str(uuid.uuid4()),
        "resume_str": text,  # Added full resume text
        "Name": extract_name(lines),
        "Experience": " | ".join(extract_experience(lines)),
        "Ability": " | ".join(extract_ability(lines)),
        "Skill": " | ".join(sorted(extract_skills(lines))),
        "Education": " | ".join(sorted(extract_education(lines)))
    }
