from flask import Blueprint, request, jsonify, send_from_directory
import pandas as pd
from .utils import read_pdf, read_docx, parse_resume, parse_job_description, calculate_fit_score, allowed_file

main = Blueprint('main', __name__)

# Define a more comprehensive list of skills
skills_list = [
    "Python", "JavaScript", "React", "Machine Learning", "Java", "SQL", "HTML", "CSS", "MySQL",
    "ROS", "C", "C++", "R", "Creativity", "Docker", "Kubernetes", "Git", "AWS", "Azure", "GCP",
    "Node.js", "TypeScript", "Scala", "Hadoop", "Spark", "TensorFlow", "PyTorch", "Swift", "Kotlin",
    "PHP", "Ruby", "Perl", "Excel", "Power BI", "Tableau", "Go", "Rust", "Jupyter", "NumPy", "Pandas",
    "Matplotlib", "Seaborn", "OpenCV", "NLTK", "SpaCy", "FastAPI", "Flask", "Django"
]

@main.route('/upload', methods=['POST'])
def upload_file():
    if 'files' not in request.files:
        return jsonify({"error": "No file part"}), 400

    files = request.files.getlist('files')
    extracted_data = []

    if not files:
        return jsonify({"error": "No selected files"}), 400

    for file in files:
        if file.filename == '':
            continue

        if file and file.filename.lower().endswith('.pdf'):
            resume_text = read_pdf(file)
        elif file and file.filename.lower().endswith('.docx'):
            resume_text = read_docx(file)
        elif file and file.filename.lower().endswith('.txt'):
            resume_text = file.read().decode('utf-8')
        else:
            continue

        extracted_info = parse_resume(resume_text)
        extracted_data.append(extracted_info)

    # Save extracted data to Excel file
    df = pd.DataFrame(extracted_data)
    output_path = 'static/extracted_data.xlsx'
    df.to_excel(output_path, index=False)

    return jsonify(extracted_data)

@main.route('/upload-job', methods=['POST'])
def upload_job():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    if file and allowed_file(file.filename):
        # Parse the job description file
        job_data = parse_job_description(file)
        return jsonify(job_data)
    
    return jsonify({'error': 'Invalid file format'}), 400

@main.route('/shortlist', methods=['POST'])
def shortlist_candidates():
    job_data = request.json['job_data']
    resumes = request.json['resumes']
    
    threshold = 10  # Set the threshold for scoring

    shortlisted = []
    for resume in resumes:
        score = calculate_fit_score(job_data, resume)
        if score > threshold:
            shortlisted.append(resume)
    
    # Save shortlisted candidates to an Excel file
    df = pd.DataFrame(shortlisted)
    df.to_excel('static/shortlisted_candidates.xlsx', index=False)
    
    return jsonify(shortlisted)

@main.route('/static/<path:filename>')
def download_file(filename):
    return send_from_directory('static', filename)
