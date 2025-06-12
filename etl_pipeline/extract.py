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
from langdetect import detect
from typing import Union

# pytesseract.pytesseract.tesseract_cmd = r""

# Load NLP model with error handling
try:
    nlp = spacy.load("en_core_web_sm")
except Exception as e:
    print(f"Error loading Spacy NLP model: {e}")
    nlp = None

# Keywords for different resume sections
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
EDUCATION_KEYWORDS = {"education", "degree", "university", "college", "coursework", "courses"}
EXPERIENCE_KEYWORDS = {"intern", "assistant", "manager", "developer", "engineer", "analyst", "consultant"}
ABILITY_KEYWORDS = ["developing", "creating", "building", "researching", "automating", "testing"]
DATE_PATTERN = r'([A-Za-z]{3,10})\s*(\d{4})'


def detect_language(text: str) -> None:
    """Detects if the text is in English, raises an error if not."""
    try:
        sanitized_text = re.sub(r"\S+@\S+|\+\d{9,}|http\S+", "", text) 
        lang = detect(sanitized_text)
        if lang != "en":
            raise ValueError("Error: Resume must be in English.")
    except Exception as e:
        raise ValueError(f"Error detecting language: {e}")

def extract_text(input_data: Union[str, Path]) -> str:
    try:
        path = Path(input_data)
        if path.exists():
            if path.suffix.lower() == ".pdf":
                extracted = extract_text_from_pdf(path)
            # elif path.suffix.lower() in [".jpg", ".jpeg", ".png", ".tiff"]:
            #     extracted = extract_text_via_ocr(path)
            else:
                raise ValueError(f"Unsupported file format: {path.suffix}")
            return clean_text(extracted)

        # If it's not a file, assume it's raw resume string
        return clean_text(str(input_data))

    except Exception as e:
        raise RuntimeError(f"Error extracting text: {e}")



def extract_text_from_pdf(pdf_path: Union[str, Path]) -> str:
    """Extract text from a PDF using pdfplumber, fallback to OCR if necessary."""
    try:
        text_blocks = []
        with pdfplumber.open(str(pdf_path)) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text_blocks.append(extracted)

        if not text_blocks:
            return extract_text_via_ocr(pdf_path)

        full_text = "\n".join(text_blocks)
        detect_language(full_text)  # Raise error if not English
        return full_text.strip()

    except Exception as e:
        raise RuntimeError(f"Error extracting text from PDF: {e}")



def extract_text_via_ocr(image_path: Union[str, Path]) -> str:
    """Extract text using OCR from scanned PDFs or images."""
    try:
        text = ""
        if image_path.suffix.lower() == ".pdf":
            images = convert_from_path(str(image_path))
            for img in images:
                text += pytesseract.image_to_string(img) + "\n"
        else:
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img)

        return clean_text(text)
    except Exception as e:
        raise RuntimeError(f"Error extracting text via OCR: {e}")


def clean_text(text: str) -> str:
    """Cleans text by removing extra characters."""
    try:
        text = re.sub(r'(\\n|\\r|\\t|\n|\r|\t)+', '\n', text)
        text = re.sub(r'[▪️\-\[\]●+•.:|\'%]', '', text)
        return text.strip()
    except Exception as e:
        raise RuntimeError(f"Error cleaning text: {e}")

def extract_name(lines):
    """Extracts name from resume header using NLP."""
    try:
        for line in lines[:5]:
            clean_line = line.strip()
            if clean_line and not any(char.isdigit() for char in clean_line):
                return clean_line
        if nlp is None:
            return "Unknown"
        doc = nlp("\n".join(lines[:5]))
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                return ent.text.strip()
        return "Unknown"
    except Exception as e:
        raise RuntimeError(f"Error extracting name: {e}")


def extract_skills(lines):
    try:
        skill_block = False
        extracted_skills = set()

        for line in lines:
            lower_line = line.lower()
            if "skill" in lower_line or "skills" in lower_line or "technical skills" in lower_line or "programming language" in lower_line or "soft skills" in lower_line or "languages" in lower_line:
                skill_block = True
                continue
            if skill_block and any(kw in lower_line for kw in ["experience", "certification", "project", "skills", "certificate"]):
                skill_block = False
            if skill_block:
                extracted_skills.update(re.findall(r'\b[a-zA-Z0-9+#.]+\b', lower_line))
        filtered_skills = {skill.strip() for skill in extracted_skills if skill.lower() not in ["and"]}

        return filtered_skills
    except Exception as e:
        raise RuntimeError(f"Error extracting skills: {e}")


def extract_education(lines):
    """Extracts education details dynamically based on keywords and calculates duration."""
    try:
        education_entries = []
        edu_block = False
        start_year = None

        for line in lines:
            lower_line = line.lower().strip()
            if any(ek in lower_line for ek in EDUCATION_KEYWORDS):
                edu_block = True
                education_entries.append(line.strip()) 
                continue
            if edu_block and any(kw in lower_line for kw in ["experience", "certification", "project", "skills", "projects"]):
                edu_block = False
            match = re.search(DATE_PATTERN, line) 
            if edu_block and match:
                if start_year is None:
                    start_year = match.group(1)
                else:
                    end_year = match.group(1)
                    duration = calculate_months(f"Jan {start_year}", f"Dec {end_year}")
                    education_entries.append(f"{line.strip()}")
                    start_year = None 

        return education_entries
    except Exception as e:
        raise RuntimeError(f"Error extracting education: {e}")


def extract_experience(lines):
    """Extracts job titles and durations dynamically."""
    try:
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
    except Exception as e:
        raise RuntimeError(f"Error extracting experience: {e}")

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
    
def preprocess_lines(text: str) -> list:
    """Improves structure detection by reconstructing logical lines from raw text."""
    try:
        # Normalize bullet points and random indents
        text = re.sub(r'[\u2022•·◦●►]', '\n', text)
        text = re.sub(r'(?<=[a-z])\s{2,}(?=[A-Z])', '\n', text)  # Break lines between lower and upper case
        text = re.sub(r'\n{2,}', '\n', text)
        return [line.strip() for line in text.splitlines() if line.strip()]
    except Exception as e:
        raise RuntimeError(f"Error preprocessing lines: {e}")



def extract_resume_features(input_data: Union[str, Path]) -> dict:
    """Extracts structured details from a resume, accepting either a file or raw string."""
    try:
        text = extract_text(input_data)
        lines = preprocess_lines(text)

        return {
            "ID": str(uuid.uuid4()),
            "resume_str": text,
            "Name": extract_name(lines),
            "Experience": ", ".join(extract_experience(lines)),
            "skill": ", ".join(extract_skills(lines)),
            "ability": ", ".join(extract_ability(lines)),
            "program": ", ".join(extract_education(lines))
        }
    except Exception as e:
        raise RuntimeError(f"Error extracting resume features: {e}")