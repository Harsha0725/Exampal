# 🎓 ExamPal: AI-Powered Question Paper & Marking Scheme Generator

**ExamPal** is an institutional-grade, enterprise EdTech SaaS application built with Python, Streamlit, Google Gemini API, PyPDF, Plotly, and FPDF2. It transforms textbook chapters, syllabi, or lecture notes into formal examination papers along with complete teacher answer keys and step-by-step grading rubrics.

---

## ✨ Features & Highlights

- **🏛️ Institutional Grade Formatting:** Generates clean, formal exam papers with customizable school/university headers, general instructions, section breaks, and time/marks constraints.
- **🗝️ Comprehensive Teacher Marking Scheme:** Generates detailed model answers, numerical step-by-step solutions, and point-by-point grading rubrics.
- **📄 Dual PDF Export Engine:** Built with `fpdf2` to dynamically compile downloadable PDFs for both **Student Question Papers** and **Teacher Answer Keys**.
- **📊 Interactive Visual Analytics:** Uses Plotly charts to display marks distribution across sections, difficulty levels (🟢 Easy, 🟡 Medium, 🔴 Hard), and Bloom's Taxonomy cognitive levels.
- **⚡ Dual Source Material Inputs:** Upload any syllabus or textbook PDF (`pypdf` text extraction) OR paste raw topic text directly. Includes a 1-click sample dataset button for instant testing.
- **🎨 Enterprise Dark Theme & Styling:** Custom CSS design featuring glassmorphism elements, vibrant metric counters, badges, and responsive layouts.

---

## 🛠️ Technology Stack

- **Frontend & App Framework:** [Streamlit](https://streamlit.io/)
- **AI Core:** [Google Gemini API (`google-genai`)](https://github.com/google-gemini/deprecations)
- **PDF Generation Engine:** [FPDF2 (`fpdf2`)](https://pyfpdf.github.io/fpdf2/)
- **PDF Extraction:** [PyPDF (`pypdf`)](https://pypdf.readthedocs.io/)
- **Visual Analytics:** [Plotly Express (`plotly`)](https://plotly.com/python/)
- **Environment Management:** `python-dotenv`

---

## 🚀 Quick Start & Installation

### 1. Clone or Open Project Directory
```bash
cd exampal
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Key
Copy `.env.example` to `.env` and enter your Gemini API key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```
*(Alternatively, you can enter your API Key directly inside the app sidebar input).*

### 4. Run the Streamlit Application
```bash
streamlit run app.py
```

---

## 📄 Output Schema (Strict JSON Structure)

The application enforces structured JSON output matching this institutional format:

```json
{
  "exam_meta": {
    "institution_name": "Global Academy of Technology",
    "exam_title": "Mid-Term Examination 2026",
    "subject": "Class 10 Science",
    "grade": "Grade 10 - Section A",
    "total_marks": 50,
    "duration_minutes": 90,
    "instructions": ["Read all questions carefully."]
  },
  "sections": [
    {
      "section_name": "Section A: Multiple Choice Questions",
      "section_type": "MCQ",
      "questions": [
        {
          "question_id": "Q1",
          "type": "MCQ",
          "question_text": "Which of the following is a displacement reaction?",
          "options": ["A) Zn + CuSO4 -> ZnSO4 + Cu", "B) 2H2 + O2 -> 2H2O"],
          "marks": 1,
          "difficulty": "Easy",
          "blooms_level": "Remembering",
          "model_answer": "A) Zn + CuSO4 -> ZnSO4 + Cu",
          "marking_rubric": "1 mark for identifying the correct option."
        }
      ]
    }
  ]
}
```

---

## 📂 Project Structure

```
exampal/
├── app.py              # Main Streamlit web application & PDF export engine
├── requirements.txt    # Required Python dependencies
├── .env                # Local environment variables (GEMINI_API_KEY)
├── .env.example        # Environment template file
└── README.md           # Documentation walkthrough
```

---

## 🛡️ License

Built for educational institutions, teachers, and EdTech platforms.
