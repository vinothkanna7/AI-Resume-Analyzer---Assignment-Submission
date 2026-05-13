# AI-Resume-Analyzer---Assignment-Submission
This project is a web-based AI Resume Analyzer application that allows users to upload resumes in PDF format and receive AI-generated feedback. The application extracts text from resumes, analyzes the content using OpenAI models, and provides structured insights such as resume score, strengths, weaknesses, missing areas, and improvement suggestions

# Project Architecture
User Uploads Resume (PDF)
        ↓
Frontend (HTML Form)
        ↓
Flask Backend
        ↓
PDF Text Extraction
        ↓
OpenAI API Analysis
        ↓
Structured JSON Response
        ↓
Results Page

# Tech Stack
Frontend :	HTML, CSS, JS
Backend	  : Python Flask
AI	:  OpenAI Platform
Resume Parsing	: pdfplumber
Environment	:  Python venv
API Handling :  openai Python SDK

# Folder Structure
resume-analyzer/
│
├── app.py
├── requirements.txt
├── README.md
├── .env
│
├── templates/
│   ├── index.html
│   └── result.html
│
├── static/
│   └── style.css
│
└── uploads/

# Step 1 — Install Dependencies
## requirements.txt 
flask
openai
pdfplumber
python-dotenv

pip install -r requirements.txt

# Step 2 — Create Frontend

## templates/index.html

<!DOCTYPE html>
<html>
<head>
    <title>AI Resume Analyzer</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>

<div class="container">
    <h1>AI Resume Analyzer</h1>

    <form action="/analyze" method="POST" enctype="multipart/form-data">
        <input type="file" name="resume" accept=".pdf" required>
        <button type="submit">Analyze Resume</button>
    </form>
</div>

</body>
</html>

# Step 3 — Result Page

## templates/result.html
<!DOCTYPE html>
<html>
<head>
    <title>Resume Analysis</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>

<div class="container">

    <h1>Resume Analysis Result</h1>

    <h2>Overall Score: {{ result.score }}/100</h2>

    <h3>Profile Summary</h3>
    <p>{{ result.summary }}</p>

    <h3>Strengths</h3>
    <ul>
        {% for item in result.strengths %}
        <li>{{ item }}</li>
        {% endfor %}
    </ul>

    <h3>Weaknesses</h3>
    <ul>
        {% for item in result.weaknesses %}
        <li>{{ item }}</li>
        {% endfor %}
    </ul>

    <h3>Missing Areas</h3>
    <ul>
        {% for item in result.missing_areas %}
        <li>{{ item }}</li>
        {% endfor %}
    </ul>

    <h3>Suggestions</h3>
    <ul>
        {% for item in result.suggestions %}
        <li>{{ item }}</li>
        {% endfor %}
    </ul>

</div>

</body>
</html>

# static/style.css

body {
    font-family: Arial;
    background: #f5f5f5;
}

.container {
    width: 70%;
    margin: auto;
    margin-top: 40px;
    background: white;
    padding: 30px;
    border-radius: 10px;
}

button {
    padding: 10px 20px;
    cursor: pointer;
}

# Step 5 — Backend Flask App
# app.py

from flask import Flask, render_template, request
import pdfplumber
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

UPLOAD_FOLDER = "uploads"


def extract_text_from_pdf(pdf_path):
    text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()

            if extracted:
                text += extracted + "\n"

    return text


def analyze_resume(resume_text):

    prompt = f"""
    Analyze the following resume.

    Return response ONLY in JSON format.

    Required JSON structure:

    {{
      "score": number,
      "summary": "string",
      "strengths": ["point1", "point2"],
      "weaknesses": ["point1", "point2"],
      "missing_areas": ["point1", "point2"],
      "suggestions": ["point1", "point2"]
    }}

    Resume:
    {resume_text}
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an expert resume reviewer."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    content = response.choices[0].message.content

    return json.loads(content)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():

    file = request.files["resume"]

    if not file:
        return "No file uploaded"

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)

    file.save(filepath)

    resume_text = extract_text_from_pdf(filepath)

    result = analyze_resume(resume_text)

    return render_template("result.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)

# Step 6 — Environment Variables

# .env
OPENAI_API_KEY=your_api_key_here

# Step 7 — Run Project
