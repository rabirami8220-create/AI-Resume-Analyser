from flask import Flask,render_template,request
import google.generativeai as genai
import os
from pypdf import PdfReader
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

app = Flask(__name__)
UPLOAD_FOLDER = 'resumes'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configure the Generative AI model
load_dotenv()  # Load environment variables from .env file
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")
def extract_text(filepath):
    if filepath.lower().endswith('.pdf'):
        reader = PdfReader(filepath)
        text = ''
        for page in reader.pages:
            text += page.extract_text() or ''
        return text
    else:
        with open(filepath, 'r', encoding='utf-8',errors='ignore') as file:
            return file.read()
@app.route('/')
def home():
    return render_template('index.html')
@app.route('/analyse', methods=['POST'])
def analyse():
    uploaded_file = request.files.get('resume')
    if not uploaded_file or uploaded_file.filename == '':
        return "please select your resume"
    filename = secure_filename(uploaded_file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    uploaded_file.save(filepath)
    try:
        resume=extract_text(filepath)
    except Exception as e:
        return f"could not read file:{e}"
    if not resume.strip():
        return "could not extract any text from the file.Try a different resume."
    prompt=f""" you are an experienced technical recruiter and resume reviewer.Do not use markdown formatting like asterisks or hashtags,just plain text.
    Analyse the following resume and respond in this exact format:
    score:X/10
    strengths:
    -point 1
    -point 2
    weaknesses:
    -point 1
    -point 2
    suggestions for improvement:
    -point 1
    -point 2
    Resume:
    {resume}
    """
    try:
        response = model.generate_content(prompt)
        result = response.text
    except Exception as e:
        result = str(e)
    return render_template('result.html', response=result)
if __name__ == '__main__':
    app.run(debug=True)