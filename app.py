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
