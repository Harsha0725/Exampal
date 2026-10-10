import os
import json
import re
import io
import time
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from pypdf import PdfReader
from fpdf import FPDF, XPos, YPos
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

# ==========================================
# PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(
    page_title="ExamPal | AI Question Paper & Marking Scheme Generator",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Enterprise EdTech SaaS CSS & Theme Engine
def get_theme_css(theme_choice: str) -> str:
    if "Light" in theme_choice:
        vars_css = """
        :root {
            --bg-app: #F8FAFC;
            --text-main: #0F172A;
            --card-bg: #FFFFFF;
            --card-border: #CBD5E1;
            --banner-bg: linear-gradient(135deg, #3730A3 0%, #4F46E5 50%, #6366F1 100%);
            --hero-title-grad: linear-gradient(90deg, #FFFFFF, #E0E7FF, #C7D2FE);
            --hero-subtitle: #E0E7FF;
            --metric-val: #0F172A;
            --metric-lbl: #475569;
            --qbox-bg: #FFFFFF;
            --qbox-border: #CBD5E1;
            --qbox-title: #0F172A;
            --mcq-bg: #F1F5F9;
            --mcq-text: #1E293B;
            --rubric-bg: #ECFDF5;
            --answer-bg: #EFF6FF;
            --sidebar-bg: #F8FAFC;
            --sidebar-border: #CBD5E1;
            --badge-blooms-text: #4F46E5;
            --badge-marks-text: #0284C7;
        }
        """
    elif "Dark" in theme_choice:
        vars_css = """
        :root {
            --bg-app: #0F172A;
            --text-main: #F8FAFC;
            --card-bg: rgba(30, 41, 59, 0.7);
            --card-border: rgba(255, 255, 255, 0.08);
            --banner-bg: linear-gradient(135deg, #1E1B4B 0%, #312E81 50%, #4338CA 100%);
            --hero-title-grad: linear-gradient(90deg, #A5B4FC, #C084FC, #818CF8);
            --hero-subtitle: #94A3B8;
            --metric-val: #F1F5F9;
            --metric-lbl: #94A3B8;
            --qbox-bg: #1E293B;
            --qbox-border: #334155;
            --qbox-title: #F8FAFC;
            --mcq-bg: #0F172A;
            --mcq-text: #E2E8F0;
            --rubric-bg: rgba(15, 23, 42, 0.6);
            --answer-bg: rgba(30, 58, 138, 0.25);
            --sidebar-bg: #0B1120;
            --sidebar-border: #1E293B;
            --badge-blooms-text: #A5B4FC;
            --badge-marks-text: #38BDF8;
        }
        """
    else:  # System (detects light/dark mode preference from browser/OS)
        vars_css = """
        @media (prefers-color-scheme: light) {
            :root {
                --bg-app: #F8FAFC;
                --text-main: #0F172A;
                --card-bg: #FFFFFF;
                --card-border: #CBD5E1;
                --banner-bg: linear-gradient(135deg, #3730A3 0%, #4F46E5 50%, #6366F1 100%);
                --hero-title-grad: linear-gradient(90deg, #FFFFFF, #E0E7FF, #C7D2FE);
                --hero-subtitle: #E0E7FF;
                --metric-val: #0F172A;
                --metric-lbl: #475569;
                --qbox-bg: #FFFFFF;
                --qbox-border: #CBD5E1;
                --qbox-title: #0F172A;
                --mcq-bg: #F1F5F9;
                --mcq-text: #1E293B;
                --rubric-bg: #ECFDF5;
                --answer-bg: #EFF6FF;
                --sidebar-bg: #F8FAFC;
                --sidebar-border: #CBD5E1;
                --badge-blooms-text: #4F46E5;
                --badge-marks-text: #0284C7;
            }
        }
        @media (prefers-color-scheme: dark) {
            :root {
                --bg-app: #0F172A;
                --text-main: #F8FAFC;
                --card-bg: rgba(30, 41, 59, 0.7);
                --card-border: rgba(255, 255, 255, 0.08);
                --banner-bg: linear-gradient(135deg, #1E1B4B 0%, #312E81 50%, #4338CA 100%);
                --hero-title-grad: linear-gradient(90deg, #A5B4FC, #C084FC, #818CF8);
                --hero-subtitle: #94A3B8;
                --metric-val: #F1F5F9;
                --metric-lbl: #94A3B8;
                --qbox-bg: #1E293B;
                --qbox-border: #334155;
                --qbox-title: #F8FAFC;
                --mcq-bg: #0F172A;
                --mcq-text: #E2E8F0;
                --rubric-bg: rgba(15, 23, 42, 0.6);
                --answer-bg: rgba(30, 58, 138, 0.25);
                --sidebar-bg: #0B1120;
                --sidebar-border: #1E293B;
                --badge-blooms-text: #A5B4FC;
                --badge-marks-text: #38BDF8;
            }
        }
        """
    return f"<style>{vars_css}</style>"

CUSTOM_CSS = """
<style>
    /* Global Font & Variable Overrides */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main Background & Base Text Color */
    .stApp {
        background-color: var(--bg-app) !important;
        color: var(--text-main) !important;
    }

    /* Target Streamlit Text & Headers */
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, 
    .stApp p, .stApp label, .stMarkdown, div[data-testid="stMarkdownContainer"] p {
        color: var(--text-main);
    }
    
    /* App Banner Header */
    .hero-banner {
        background: var(--banner-bg);
        border: 1px solid var(--card-border);
        border-radius: 16px;
        padding: 28px 36px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.15), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
    }
    
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: var(--hero-title-grad);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 6px 0;
    }
    
    .hero-subtitle {
        color: var(--hero-subtitle);
        font-size: 1.05rem;
        font-weight: 400;
        margin: 0;
    }
    
    /* Metric Counter Cards */
    .metric-card {
        background: var(--card-bg);
        backdrop-filter: blur(12px);
        border: 1px solid var(--card-border);
        border-radius: 14px;
        padding: 18px 22px;
        text-align: center;
        transition: transform 0.2s ease, border-color 0.2s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.5);
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: var(--metric-val);
        margin: 4px 0;
    }
    
    .metric-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--metric-lbl);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Badges */
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 6px;
    }
    
    .badge-easy {
        background-color: rgba(16, 185, 129, 0.15);
        color: #10B981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    .badge-medium {
        background-color: rgba(245, 158, 11, 0.15);
        color: #F59E0B;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    
    .badge-hard {
        background-color: rgba(239, 68, 68, 0.15);
        color: #EF4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }

    .badge-blooms {
        background-color: rgba(99, 102, 241, 0.15);
        color: var(--badge-blooms-text);
        border: 1px solid rgba(99, 102, 241, 0.3);
    }

    .badge-marks {
        background-color: rgba(14, 165, 233, 0.15);
        color: var(--badge-marks-text);
        border: 1px solid rgba(14, 165, 233, 0.3);
    }

    /* Question Cards */
    .question-box {
        background: var(--qbox-bg);
        border: 1px solid var(--qbox-border);
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 16px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03);
    }

    .question-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }

    .question-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--qbox-title);
    }

    .mcq-option {
        background: var(--mcq-bg);
        border: 1px solid var(--qbox-border);
        padding: 10px 14px;
        border-radius: 8px;
        margin-top: 8px;
        font-size: 0.95rem;
        color: var(--mcq-text);
    }

    /* Rubric & Answer Callout Boxes */
    .rubric-box {
        background: var(--rubric-bg);
        border-left: 4px solid #10B981;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin-top: 10px;
        font-size: 0.9rem;
        color: var(--text-main);
    }

    .answer-box {
        background: var(--answer-bg);
        border-left: 4px solid #3B82F6;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin-top: 10px;
        font-size: 0.92rem;
        color: var(--text-main);
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: var(--sidebar-bg) !important;
        border-right: 1px solid var(--sidebar-border) !important;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%);
        color: #FFFFFF !important;
        font-weight: 600;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        transition: all 0.2s ease;
    }

    .stButton>button:hover {
        background: linear-gradient(135deg, #4338CA 0%, #4F46E5 100%);
        box-shadow: 0 4px 14px rgba(79, 70, 229, 0.4);
    }
</style>
"""



# ==========================================
# HELPER FUNCTIONS & SANITIZATION
# ==========================================

def clean_pdf_text(text: str) -> str:
    """Sanitizes text for FPDF standard font compatibility (latin-1 fallback)."""
    if not text:
        return ""
    replacements = {
        '—': '-', '–': '-', '“': '"', '”': '"', '‘': "'", '’': "'",
        '…': '...', '•': '*', '°': ' deg', 'µ': 'u', '±': '+/-',
        '™': '(TM)', '®': '(R)', '©': '(C)', '≠': '!=', '≤': '<=', '≥': '>=',
        '→': '->', '←': '<-', '×': 'x', '÷': '/', '🔴': '[Hard]',
        '🟡': '[Med]', '🟢': '[Easy]', '🧠': '', '💡': 'Answer:', '📋': 'Rubric:'
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)
    return text.encode('latin-1', 'replace').decode('latin-1')

def extract_text_from_pdf(pdf_file) -> str:
    """Extracts raw text from an uploaded PDF file."""
    try:
        reader = PdfReader(pdf_file)
        extracted_text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                extracted_text += content + "\n"
        return extracted_text.strip()
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return ""

def load_sample_topics() -> str:
    """Returns sample syllabus topic content for quick 1-click testing."""
    return """
Subject: Class 10 Science (Chemistry & Physics)

Chapter 1: Chemical Reactions and Equations
- Chemical equations, balancing chemical equations, implications of a balanced chemical equation.
- Types of chemical reactions: combination, decomposition, displacement, double displacement, precipitation, neutralization, oxidation and reduction.
- Effects of oxidation reactions in everyday life: corrosion and rancidity.

Chapter 2: Acids, Bases and Salts
- Definitions based on furnishing of H+ and OH- ions, general properties, examples and uses.
- Neutralization, concept of pH scale (Definition relating to logarithm not required), importance of pH in everyday life.
- Preparation and uses of Sodium Hydroxide, Bleaching powder, Baking soda, Washing soda and Plaster of Paris.

Chapter 3: Light - Reflection and Refraction
- Reflection of light by curved surfaces; Images formed by spherical mirrors, centre of curvature, principal axis, principal focus, focal length, mirror formula, magnification.
- Refraction; Laws of refraction, refractive index.
- Refraction of light by spherical lens; Image formed by spherical lenses; Lens formula; Magnification; Power of a lens.
""".strip()

# ==========================================
# FPDF2 PDF GENERATION ENGINE
# ==========================================

class ExamPDF(FPDF):
    def __init__(self, institution_name, exam_title, subject, grade, duration, total_marks, is_teacher_key=False):
        super().__init__()
        self.institution_name = clean_pdf_text(institution_name)
        self.exam_title = clean_pdf_text(exam_title)
        self.subject = clean_pdf_text(subject)
        self.grade = clean_pdf_text(grade)
        self.duration = str(duration)
        self.total_marks = str(total_marks)
        self.is_teacher_key = is_teacher_key

    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.cell(self.epw, 8, self.institution_name, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        
        self.set_font("Helvetica", "B", 12)
        title_text = f"{self.exam_title} {'(TEACHER MARKING SCHEME)' if self.is_teacher_key else ''}"
        self.cell(self.epw, 7, title_text, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        
        self.set_font("Helvetica", "", 10)
        info_str = f"Subject: {self.subject}  |  Class/Grade: {self.grade}"
        self.cell(self.epw, 6, info_str, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        
        time_marks_str = f"Time Allowed: {self.duration} Minutes  |  Maximum Marks: {self.total_marks}"
        self.cell(self.epw, 6, time_marks_str, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        
        # Double Line Separator
        self.set_draw_color(50, 50, 50)
        self.line(10, self.get_y() + 2, 200, self.get_y() + 2)
        self.line(10, self.get_y() + 3.5, 200, self.get_y() + 3.5)
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(100, 100, 100)
        footer_label = "ExamPal AI Generated Paper" if not self.is_teacher_key else "ExamPal Teacher Marking Scheme - Confidential"
        self.cell(self.epw, 10, f"{footer_label}  |  Page {self.page_no()}/{{nb}}", align="C")

def build_student_pdf(exam_data: dict) -> bytes:
    meta = exam_data.get("exam_meta", {})
    pdf = ExamPDF(
        institution_name=meta.get("institution_name", "School/University"),
        exam_title=meta.get("exam_title", "Examination"),
        subject=meta.get("subject", "General Subject"),
        grade=meta.get("grade", "Grade 10"),
        duration=meta.get("duration_minutes", 90),
        total_marks=meta.get("total_marks", 50),
        is_teacher_key=False
    )
    pdf.alias_nb_pages()
    pdf.add_page()

    # General Instructions Box
    instructions = meta.get("instructions", [])
    if instructions:
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(pdf.epw, 6, "General Instructions:", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", "", 9)
        for idx, inst in enumerate(instructions, 1):
            pdf.multi_cell(pdf.epw, 5, clean_pdf_text(f"  {idx}. {inst}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(4)

    # Sections & Questions
    for section in exam_data.get("sections", []):
        sec_name = clean_pdf_text(section.get("section_name", "Section"))
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_fill_color(240, 240, 245)
        pdf.cell(pdf.epw, 7, f" {sec_name.upper()} ", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(3)

        for q in section.get("questions", []):
            q_id = clean_pdf_text(q.get("question_id", "Q"))
            q_text = clean_pdf_text(q.get("question_text", ""))
            marks = q.get("marks", 1)
            
            pdf.set_font("Helvetica", "B", 10)
            pdf.multi_cell(pdf.epw, 5, f"{q_id}. {q_text}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
            # Print Options if MCQ
            options = q.get("options", [])
            if options:
                pdf.ln(1)
                pdf.set_font("Helvetica", "", 9.5)
                for opt in options:
                    pdf.multi_cell(pdf.epw, 5, clean_pdf_text(f"     {opt}"), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
            # Right aligned marks tag
            pdf.set_font("Helvetica", "I", 8.5)
            pdf.set_text_color(80, 80, 80)
            pdf.cell(pdf.epw, 5, f"[{marks} Mark{'s' if marks > 1 else ''}]", align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(3)

    return bytes(pdf.output())

def build_teacher_pdf(exam_data: dict) -> bytes:
    meta = exam_data.get("exam_meta", {})
    pdf = ExamPDF(
        institution_name=meta.get("institution_name", "School/University"),
        exam_title=meta.get("exam_title", "Examination"),
        subject=meta.get("subject", "General Subject"),
        grade=meta.get("grade", "Grade 10"),
        duration=meta.get("duration_minutes", 90),
        total_marks=meta.get("total_marks", 50),
        is_teacher_key=True
    )
    pdf.alias_nb_pages()
    pdf.add_page()

    for section in exam_data.get("sections", []):
        sec_name = clean_pdf_text(section.get("section_name", "Section"))
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_fill_color(230, 245, 235)
        pdf.cell(pdf.epw, 7, f" {sec_name.upper()} - MARKING SCHEME ", fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(3)

        for q in section.get("questions", []):
            q_id = clean_pdf_text(q.get("question_id", "Q"))
            q_text = clean_pdf_text(q.get("question_text", ""))
            model_ans = clean_pdf_text(q.get("model_answer", "N/A"))
            rubric = clean_pdf_text(q.get("marking_rubric", "N/A"))
            marks = q.get("marks", 1)

            pdf.set_font("Helvetica", "B", 10)
            pdf.multi_cell(pdf.epw, 5, f"{q_id}. {q_text}  [{marks} Marks]", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            # Answer
            pdf.ln(1)
            pdf.set_font("Helvetica", "B", 9.5)
            pdf.set_text_color(16, 122, 87) # Emerald green accent
            pdf.multi_cell(pdf.epw, 5, f"Model Answer: {model_ans}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            # Rubric
            pdf.set_font("Helvetica", "I", 9)
            pdf.set_text_color(30, 64, 175) # Blue accent
            pdf.multi_cell(pdf.epw, 5, f"Grading Rubric: {rubric}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(4)

    return bytes(pdf.output())

# ==========================================
# GEMINI GENERATION LOGIC
# ==========================================

def generate_exam_json(api_key: str, model_name: str, institution: str, title: str, subject: str, grade: str,
                       total_marks: int, duration: int, text_content: str, easy_p: int, med_p: int, hard_p: int,
                       q_types: list) -> dict:
    
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
You are an expert Chief Examiner and Academic Assessment Specialist.
Generate a formal, balanced, institutional examination paper and teacher marking scheme based ONLY on the following source material.

--- EXAM METADATA ---
Institution Name: {institution}
Exam Title: {title}
Subject: {subject}
Class/Grade: {grade}
Total Marks Target: {total_marks}
Exam Duration: {duration} Minutes
Target Difficulty Balance: {easy_p}% Easy, {med_p}% Medium, {hard_p}% Hard
Allowed Question Types: {', '.join(q_types)}

--- SOURCE SYLLABUS / TEXTBOOK CONTENT ---
{text_content}

--- STRICT OUTPUT FORMAT REQUIREMENT ---
You MUST respond with valid JSON ONLY. No preamble, no markdown backticks, no markdown text outside the JSON.
The JSON must follow this exact structure:

{{
  "exam_meta": {{
    "institution_name": "{institution}",
    "exam_title": "{title}",
    "subject": "{subject}",
    "grade": "{grade}",
    "total_marks": {total_marks},
    "duration_minutes": {duration},
    "instructions": [
      "Read all questions carefully before answering.",
      "Section A contains objective multiple choice questions.",
      "Section B contains short answer conceptual questions.",
      "Section C contains analytical and long answer case-study questions.",
      "All questions are compulsory."
    ]
  }},
  "sections": [
    {{
      "section_name": "Section A: Multiple Choice Questions",
      "section_type": "MCQ",
      "questions": [
        {{
          "question_id": "Q1",
          "type": "MCQ",
          "question_text": "Clear objective question stem?",
          "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
          "marks": 1,
          "difficulty": "Easy",
          "blooms_level": "Remembering",
          "model_answer": "A) Option 1",
          "marking_rubric": "1 Mark for selecting the correct option A."
        }}
      ]
    }},
    {{
      "section_name": "Section B: Short Answer Questions",
      "section_type": "Short Answer",
      "questions": [
        {{
          "question_id": "Q5",
          "type": "Short Answer",
          "question_text": "Conceptual short answer question?",
          "options": [],
          "marks": 3,
          "difficulty": "Medium",
          "blooms_level": "Understanding",
          "model_answer": "Detailed comprehensive model answer explaining concepts...",
          "marking_rubric": "+1 mark for definition, +1 mark for formula, +1 mark for example."
        }}
      ]
    }},
    {{
      "section_name": "Section C: Long Answer / Case Studies",
      "section_type": "Long Answer",
      "questions": [
        {{
          "question_id": "Q9",
          "type": "Long Answer",
          "question_text": "In-depth analytical or case study question?",
          "options": [],
          "marks": 5,
          "difficulty": "Hard",
          "blooms_level": "Applying",
          "model_answer": "Extensive step-by-step solution and explanation...",
          "marking_rubric": "+2 marks for diagram/setup, +2 marks for derivation/proof, +1 mark for conclusion."
        }}
      ]
    }}
  ]
}}

CRITICAL INSTRUCTIONS:
1. Ensure the sum of marks of ALL questions across sections EXACTLY equals {total_marks}.
2. Ensure difficulty levels (Easy, Medium, Hard) match requested proportions ({easy_p}% / {med_p}% / {hard_p}%).
3. Assign appropriate Bloom's Taxonomy levels: Remembering, Understanding, Applying, Analyzing, Evaluating, Creating.
4. Provide thorough, accurate model answers and point-by-point grading rubrics for every single question.
"""

    config = types.GenerateContentConfig(
        response_mime_type="application/json"
    )

    # Candidate models in sequence order with quota fallbacks
    candidate_models = [model_name, "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.1-flash-lite"]
    seen = set()
    unique_models = [m for m in candidate_models if not (m in seen or seen.add(m))]

    last_err = None
    for m in unique_models:
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=m,
                    contents=prompt,
                    config=config
                )
                clean_text = response.text.strip()
                if clean_text.startswith("```json"):
                    clean_text = clean_text[7:]
                if clean_text.endswith("```"):
                    clean_text = clean_text[:-3]
                clean_text = clean_text.strip()

                return json.loads(clean_text)
            except Exception as e:
                last_err = e
                err_str = str(e)
                # If 503 capacity limit, wait briefly
                if "503" in err_str or "UNAVAILABLE" in err_str:
                    time.sleep(2)
                else:
                    # If 429 quota error or 404, move to next model immediately
                    break

    raise last_err


# ==========================================
# STREAMLIT UI LAYOUT
# ==========================================

# Hero Banner
st.markdown("""
<div class="hero-banner">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <h1 class="hero-title">ExamPal 🎓</h1>
            <p class="hero-subtitle">AI-Powered Institutional Question Paper & Marking Scheme Generator</p>
        </div>
        <div style="background: rgba(255,255,255,0.1); padding: 8px 16px; border-radius: 99px; border: 1px solid rgba(255,255,255,0.2);">
            <span style="color: #38BDF8; font-weight: 600; font-size: 0.85rem;">⚡ Powered by Gemini API & FPDF2</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# Sidebar Configuration
with st.sidebar:
    st.markdown("### 🎨 Appearance & Theme")
    theme_choice = st.selectbox(
        "Select Theme",
        ["Dark 🌙", "Light ☀️", "System 🖥️"],
        index=0,
        help="Switch between Dark, Light, or System preference theme"
    )
    
    # Inject Theme & Custom CSS
    st.markdown(get_theme_css(theme_choice), unsafe_allow_html=True)
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    st.divider()
    st.markdown("### ⚙️ Exam Configuration")
    
    # API Key Input
    env_api_key = os.getenv("GEMINI_API_KEY", "")
    api_key = st.text_input("🔑 Gemini API Key", value=env_api_key, type="password", help="Enter your Google Gemini API Key")
    
    # Model Selection
    model_choice = st.selectbox(
        "🧠 Gemini Model",
        ["gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.1-flash-lite"],
        index=0,
        help="Select the AI model for examination generation"
    )
    
    st.divider()
    st.markdown("#### 🏛️ Institution Details")
    inst_name = st.text_input("Institution Name", "Global Academy of Technology")
    exam_title = st.text_input("Exam Title", "Mid-Term Examination 2026")
    subject_name = st.text_input("Subject / Course", "Class 10 Science - Chemistry & Physics")
    grade_level = st.text_input("Class / Grade Level", "Grade 10 - Section A")
    
    st.divider()
    st.markdown("#### 🎯 Exam Constraints")
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        total_marks = st.number_input("Total Marks", min_value=10, max_value=200, value=50, step=5)
    with col_m2:
        duration_mins = st.number_input("Duration (Mins)", min_value=15, max_value=360, value=90, step=15)
        
    st.divider()
    st.markdown("#### 📖 Source Material")
    input_source = st.radio("Source Input Type", ["📂 Upload PDF Document", "📝 Manual Topic Input"])
    
    extracted_text = ""
    if input_source == "📂 Upload PDF Document":
        uploaded_file = st.file_uploader("Upload Syllabus or Chapter PDF", type=["pdf"])
        if uploaded_file:
            with st.spinner("Reading & extracting PDF text..."):
                extracted_text = extract_text_from_pdf(uploaded_file)
            if extracted_text:
                st.success(f"Successfully extracted {len(extracted_text.split())} words from PDF!")
            else:
                st.error("Could not extract readable text from uploaded PDF.")
    else:
        if "topic_text" not in st.session_state:
            st.session_state.topic_text = load_sample_topics()
            
        if st.button("⚡ Load Class 10 Science Sample Topic", use_container_width=True):
            st.session_state.topic_text = load_sample_topics()
            st.toast("Sample Class 10 Science syllabus loaded!", icon="🧪")
            
        extracted_text = st.text_area("Enter Syllabus / Topics Details", value=st.session_state.topic_text, height=180)

    st.divider()
    st.markdown("#### ⚖️ Difficulty Proportions")
    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        easy_pct = st.number_input("Easy %", min_value=0, max_value=100, value=30)
    with col_d2:
        med_pct = st.number_input("Med %", min_value=0, max_value=100, value=50)
    with col_d3:
        hard_pct = st.number_input("Hard %", min_value=0, max_value=100, value=20)
        
    if (easy_pct + med_pct + hard_pct) != 100:
        st.warning(f"⚠️ Total percentage is {easy_pct + med_pct + hard_pct}%. (Recommended sum: 100%)")

    st.divider()
    st.markdown("#### 📝 Question Types")
    q_mcq = st.checkbox("Multiple Choice Questions (MCQs)", value=True)
    q_short = st.checkbox("Short Answer Questions (2-3 Marks)", value=True)
    q_long = st.checkbox("Long Answer / Case Studies (5-10 Marks)", value=True)
    
    selected_q_types = []
    if q_mcq: selected_q_types.append("MCQ (1 Mark)")
    if q_short: selected_q_types.append("Short Answer (2-3 Marks)")
    if q_long: selected_q_types.append("Long Answer / Case Studies (5-10 Marks)")

    st.divider()
    generate_btn = st.button("🚀 Generate Exam Paper", use_container_width=True, type="primary")


# ==========================================
# MAIN CONTENT & WORKFLOW
# ==========================================

if generate_btn:
    if not api_key:
        st.error("❌ Please provide a valid Gemini API Key in the sidebar.")
    elif not extracted_text.strip():
        st.error("❌ Source material is empty! Please upload a PDF or enter topic text.")
    elif not selected_q_types:
        st.error("❌ Please select at least one Question Type.")
    else:
        with st.spinner("✨ Generating Institutional Question Paper & Teacher Marking Scheme via Gemini AI..."):
            try:
                exam_json = generate_exam_json(
                    api_key=api_key,
                    model_name=model_choice,
                    institution=inst_name,
                    title=exam_title,
                    subject=subject_name,
                    grade=grade_level,
                    total_marks=total_marks,
                    duration=duration_mins,
                    text_content=extracted_text,
                    easy_p=easy_pct,
                    med_p=med_pct,
                    hard_p=hard_pct,
                    q_types=selected_q_types
                )
                st.session_state.current_exam = exam_json
                st.success("🎉 Exam Paper & Marking Scheme generated successfully!")
            except Exception as e:
                err_text = str(e)
                if "429" in err_text or "RESOURCE_EXHAUSTED" in err_text or "quota" in err_text.lower():
                    st.error("⚠️ Quota Limit Reached on current model/key! Please select another model in the sidebar dropdown (e.g. `gemini-3.7-flash` / `gemini-3.6-flash`) or paste a new Gemini API Key.")
                elif "503" in err_text or "UNAVAILABLE" in err_text or "capacity" in err_text.lower():
                    st.warning("⚠️ Google Gemini API servers are experiencing temporary high traffic (503 UNAVAILABLE). Please click **🚀 Generate Exam Paper** again in a few seconds!")
                else:
                    st.error(f"❌ Failed to generate exam paper: {err_text}")

# Display Generated Exam Dashboard
if "current_exam" in st.session_state and st.session_state.current_exam:
    exam_data = st.session_state.current_exam
    meta = exam_data.get("exam_meta", {})
    sections = exam_data.get("sections", [])

    # Top-Level Metrics Counters
    all_questions = []
    for sec in sections:
        all_questions.extend(sec.get("questions", []))

    total_q_count = len(all_questions)
    computed_marks = sum(q.get("marks", 0) for q in all_questions)

    easy_count = sum(1 for q in all_questions if q.get("difficulty", "").lower() == "easy")
    med_count = sum(1 for q in all_questions if q.get("difficulty", "").lower() in ["medium", "med"])
    hard_count = sum(1 for q in all_questions if q.get("difficulty", "").lower() == "hard")

    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    with col_stat1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Marks</div>
            <div class="metric-value">{computed_marks} Marks</div>
        </div>
        """, unsafe_allow_html=True)
    with col_stat2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Questions</div>
            <div class="metric-value">{total_q_count} Questions</div>
        </div>
        """, unsafe_allow_html=True)
    with col_stat3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Exam Duration</div>
            <div class="metric-value">{meta.get('duration_minutes', duration_mins)} Mins</div>
        </div>
        """, unsafe_allow_html=True)
    with col_stat4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Difficulty Split</div>
            <div class="metric-value" style="font-size: 1.1rem; padding-top: 8px;">
                🟢 {easy_count} | 🟡 {med_count} | 🔴 {hard_count}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # PDF Compilation
    student_pdf_bytes = build_student_pdf(exam_data)
    teacher_pdf_bytes = build_teacher_pdf(exam_data)

    # Download Buttons Toolbar
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button(
            label="📄 Download Student Question Paper (PDF)",
            data=student_pdf_bytes,
            file_name=f"{meta.get('exam_title', 'Exam')}_Question_Paper.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    with col_dl2:
        st.download_button(
            label="🗝️ Download Teacher Marking Scheme (PDF)",
            data=teacher_pdf_bytes,
            file_name=f"{meta.get('exam_title', 'Exam')}_Marking_Scheme.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # DUAL-VIEW TABS
    tab_paper, tab_scheme, tab_analytics = st.tabs([
        "📄 Student Question Paper",
        "🗝️ Teacher Marking Scheme",
        "📊 Question Distribution & Analytics"
    ])

    # ----------------------------------------------------
    # TAB 1: STUDENT QUESTION PAPER
    # ----------------------------------------------------
    with tab_paper:
        st.markdown(f"""
        <div style="text-align: center; border-bottom: 2px solid var(--qbox-border); padding-bottom: 16px; margin-bottom: 24px;">
            <h2 style="margin: 0; color: var(--text-main);">{meta.get('institution_name')}</h2>
            <h3 style="margin: 4px 0; color: #6366F1;">{meta.get('exam_title')}</h3>
            <p style="color: var(--metric-lbl); margin: 0;"><b>Subject:</b> {meta.get('subject')} &nbsp;|&nbsp; <b>Class:</b> {meta.get('grade')}</p>
            <p style="color: var(--metric-lbl); margin: 4px 0;"><b>Time Allowed:</b> {meta.get('duration_minutes')} Minutes &nbsp;|&nbsp; <b>Maximum Marks:</b> {meta.get('total_marks')}</p>
        </div>
        """, unsafe_allow_html=True)

        instructions = meta.get("instructions", [])
        if instructions:
            st.info("**General Instructions:**\n" + "\n".join([f"- {inst}" for inst in instructions]))

        for sec in sections:
            sec_title = sec.get("section_name", "Section")
            st.markdown(f"### 📌 {sec_title}")
            
            for q in sec.get("questions", []):
                q_id = q.get("question_id", "Q")
                q_text = q.get("question_text", "")
                q_diff = q.get("difficulty", "Medium")
                q_blooms = q.get("blooms_level", "Understanding")
                q_marks = q.get("marks", 1)
                options = q.get("options", [])

                diff_class = f"badge-{q_diff.lower()}" if q_diff.lower() in ["easy", "medium", "hard"] else "badge-medium"

                st.markdown(f"""
                <div class="question-box">
                    <div class="question-header">
                        <div>
                            <span class="badge {diff_class}">{q_diff}</span>
                            <span class="badge badge-blooms">🧠 {q_blooms}</span>
                        </div>
                        <span class="badge badge-marks">[{q_marks} Mark{'s' if q_marks > 1 else ''}]</span>
                    </div>
                    <div class="question-title">{q_id}. {q_text}</div>
                """, unsafe_allow_html=True)

                if options:
                    col_opt1, col_opt2 = st.columns(2)
                    for idx, opt in enumerate(options):
                        target_col = col_opt1 if idx % 2 == 0 else col_opt2
                        with target_col:
                            st.markdown(f'<div class="mcq-option">{opt}</div>', unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)

    # ----------------------------------------------------
    # TAB 2: TEACHER MARKING SCHEME
    # ----------------------------------------------------
    with tab_scheme:
        st.markdown(f"""
        <div style="border-bottom: 2px solid #10B981; padding-bottom: 12px; margin-bottom: 20px;">
            <h3 style="color: #10B981; margin: 0;">🗝️ Teacher Answer Key & Detailed Marking Scheme</h3>
            <p style="color: var(--metric-lbl); margin: 4px 0;">Official grading rubrics, step-by-step solutions, and point breakdown.</p>
        </div>
        """, unsafe_allow_html=True)

        for sec in sections:
            st.markdown(f"### 💡 {sec.get('section_name')}")
            for q in sec.get("questions", []):
                q_id = q.get("question_id", "Q")
                q_text = q.get("question_text", "")
                model_ans = q.get("model_answer", "N/A")
                rubric = q.get("marking_rubric", "N/A")
                q_marks = q.get("marks", 1)

                st.markdown(f"""
                <div class="question-box" style="border-left: 4px solid #10B981;">
                    <div class="question-title">{q_id}. {q_text} &nbsp;<span style="color: var(--metric-lbl); font-size:0.9rem;">[{q_marks} Marks]</span></div>
                    
                    <div class="answer-box">
                        <b style="color: #2563EB;">💡 Model Answer / Solution:</b><br>
                        {model_ans}
                    </div>
                    
                    <div class="rubric-box">
                        <b style="color: #059669;">📋 Point-by-Point Marking Rubric:</b><br>
                        {rubric}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ----------------------------------------------------
    # TAB 3: QUESTION DISTRIBUTION & ANALYTICS
    # ----------------------------------------------------
    with tab_analytics:
        st.markdown("### 📊 Exam Structure & Cognitive Distribution")

        col_ch1, col_ch2 = st.columns(2)
        chart_font_color = "#0F172A" if "Light" in theme_choice else "#F8FAFC"

        # Chart 1: Donut Chart - Marks Distribution by Section
        sec_names = [s.get("section_name", f"Section {i+1}") for i, s in enumerate(sections)]
        sec_marks = [sum(q.get("marks", 0) for q in s.get("questions", [])) for s in sections]

        fig_sec = px.pie(
            names=sec_names,
            values=sec_marks,
            hole=0.45,
            title="Marks Weightage by Section",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_sec.update_traces(textinfo="percent+label", textfont_size=12)
        fig_sec.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color=chart_font_color)

        with col_ch1:
            st.plotly_chart(fig_sec, use_container_width=True)

        # Chart 2: Difficulty Level Breakdown
        diff_data = {"Easy": easy_count, "Medium": med_count, "Hard": hard_count}
        fig_diff = px.bar(
            x=list(diff_data.keys()),
            y=list(diff_data.values()),
            labels={"x": "Difficulty Level", "y": "Number of Questions"},
            title="Question Count by Difficulty Level",
            color=list(diff_data.keys()),
            color_discrete_map={"Easy": "#34D399", "Medium": "#FBBF24", "Hard": "#F87171"}
        )
        fig_diff.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color=chart_font_color)

        with col_ch2:
            st.plotly_chart(fig_diff, use_container_width=True)

        # Chart 3: Bloom's Taxonomy Distribution
        blooms_counts = {}
        for q in all_questions:
            b_lvl = q.get("blooms_level", "Understanding")
            blooms_counts[b_lvl] = blooms_counts.get(b_lvl, 0) + 1

        fig_blooms = px.pie(
            names=list(blooms_counts.keys()),
            values=list(blooms_counts.values()),
            hole=0.4,
            title="Bloom's Taxonomy Cognitive Levels Breakdown",
            color_discrete_sequence=px.colors.sequential.Purples
        )
        fig_blooms.update_traces(textinfo="percent+label", textfont_size=12)
        fig_blooms.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color=chart_font_color)

        st.plotly_chart(fig_blooms, use_container_width=True)

else:
    # Initial state helper banner
    st.info("👈 Use the sidebar on the left to configure your exam parameters and click **🚀 Generate Exam Paper** to begin!")
