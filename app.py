from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import re
import PyPDF2
import docx
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

# Define a comprehensive list of skills
primary_skills_list = [
    "Python", "JavaScript", "React", "Machine Learning", "Java", "SQL", "HTML", "CSS", "MySQL",
    "ROS", "C", "C++", "R", "Docker", "Kubernetes", "Git", "AWS", "Azure", "GCP",
    "Node.js", "TypeScript", "Scala", "Hadoop", "Spark", "TensorFlow", "PyTorch", "Swift", "Kotlin",
    "PHP", "Ruby", "Perl", "Go", "Rust", "Jupyter", "NumPy", "Pandas",
    "Matplotlib", "Seaborn", "OpenCV", "NLTK", "SpaCy", "FastAPI", "Flask", "Django", "Vue", "Svelte",
    "NextJS", "Nuxt", "SvelteKit", "GraphQL", "Angular", "AutoCAD", "SolidWorks", "CATIA",
    "SQL Server", "MS SQL Server"
]

secondary_skills_list = [
    "Creativity", "Microsoft Office (Word, Excel)", "Good Communication Skills", "Talent Management", "Customer Sales Management",
    "Planning & Strategizing", "Presentation Skills", "Client Relationship", "Energy Level", "Photoshop", "Multi-tasking", 
    "Collaborative", "Optimistic Thinking", "Effective team leader", "Visualizing the work", "Value loyalty", 
    "Manual Testing", "Functional Testing", "Salesforce", "Jenkins", "Hudson", "Weblogic12c", "REST API", 
    "Data Deduplication", "Single Sign-On", "Secure Cipher Index", "Agriculture Management Systems", "UML"
]



def extract_name(resume_text):
    lines = resume_text.splitlines()
    name_pattern = re.compile(r"^(?:Name:\s*)?(.*?)(?:\s*profile|\s*summary|\s*objectives)?$", re.IGNORECASE)
    for line in lines:
        match = name_pattern.match(line.strip())
        if match:
            name = match.group(1).strip()
            if name:
                return name
    for line in lines:
        if line.strip():
            return line.strip()
    return "Name not found"

def extract_email(resume_text):
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, resume_text)
    return emails[0] if emails else "Email not found"

def extract_experience(text):
    experience_pattern = r'\b(\d+)(?:\+?)\s*(?:year[s]?|yrs?)\b'
    experiences = re.findall(experience_pattern, text, re.IGNORECASE)
    unique_experiences = set(experiences)
    if unique_experiences:
        return [int(exp) for exp in unique_experiences]  # Return as list of integers
    return []

def extract_skills(text):
    text_lower = text.lower()
    primary_skills = [skill for skill in primary_skills_list if skill.lower() in text_lower]
    secondary_skills = [skill for skill in secondary_skills_list if skill.lower() in text_lower and skill.lower() not in primary_skills]

    return {
        "primary_skills": primary_skills if primary_skills else ["Primary skills not found"],
        "secondary_skills": secondary_skills if secondary_skills else ["Secondary skills not found"]
    }

def extract_qualification(text):
    patterns = [
        r'(?:Education|Qualification|Degree|Graduated|Academic Background|Certification):?\s*(.*)',
        r'(?:Education|Qualification|Degree|Graduated|Academic Background|Certification)\s*:\s*(.*)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return "Qualification not found"

def parse_resume(resume_text):
    name = extract_name(resume_text)
    email = extract_email(resume_text)
    experience = extract_experience(resume_text)
    skills = extract_skills(resume_text)
    qualification = extract_qualification(resume_text)
    
    return {
        'name': name,
        'email': email,
        'experience': experience,
        'primary_skills': skills['primary_skills'],
        'secondary_skills': skills['secondary_skills'],
        'qualification': qualification
    }

def read_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text() or ''
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ''

def read_docx(file):
    try:
        doc = docx.Document(file)
        text = ''
        for para in doc.paragraphs:
            text += para.text + '\n'
        return text
    except Exception as e:
        print(f"Error reading DOCX: {e}")
        return ''

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'files' not in request.files:
            return jsonify({"error": "No file part"}), 400

        files = request.files.getlist('files')
        extracted_data = []

        if not files:
            return jsonify({"error": "No selected files"}), 400

        for file in files:
            if file.filename == '':
                continue

            file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
            
            if file_ext == 'pdf':
                resume_text = read_pdf(file)
            elif file_ext == 'docx':
                resume_text = read_docx(file)
            elif file_ext == 'txt':
                resume_text = file.read().decode('utf-8')
            else:
                continue

            parsed_data = parse_resume(resume_text)
            extracted_data.append(parsed_data)

        # Save extracted data to Excel file
        df = pd.DataFrame(extracted_data)
        output_path = os.path.join('static', 'uploads', 'extracted_resumes.xlsx')
        df.to_excel(output_path, index=False)

        return jsonify(extracted_data)
    except Exception as e:
        print(f"Error in upload_file: {e}")  # Debug statement
        return jsonify({"error": str(e)}), 500

@app.route('/upload-job', methods=['POST'])
def upload_job_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files['file']
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        
        if file_ext == 'pdf':
            job_text = read_pdf(file)
        elif file_ext == 'docx':
            job_text = read_docx(file)
        elif file_ext == 'txt':
            job_text = file.read().decode('utf-8')
        else:
            return jsonify({"error": "Invalid file format"}), 400

        job_data = parse_job_description(job_text)

        # Save job data to Excel
        df = pd.DataFrame([job_data])
        output_path = os.path.join('static','uploads', 'job_description.xlsx')
        df.to_excel(output_path, index=False)
        
        return jsonify(job_data)
    except Exception as e:
        print(f"Error in upload_job_file: {e}")  # Debug statement
        return jsonify({"error": str(e)}), 500

def parse_job_description(job_text):
    experience = extract_experience(job_text)
    skills = extract_skills(job_text)
    location_match = re.search(r'Location:\s*(.*)', job_text)
    qualification_match = re.search(r'(?:Education|Qualification|Degree|Graduated|Academic Background|Certification):?\s*(.*)', job_text)
    projects_match = re.search(r'Responsibilities:\s*(.*)', job_text)
    
    return {
        'location': location_match.group(1) if location_match else "Location not found",
        'qualification': qualification_match.group(1) if qualification_match else "Qualification not found",
        'experience': experience,
        'primary_skills': skills['primary_skills'],
        'secondary_skills': skills['secondary_skills'],
        'skill_experience_years': experience,
        'projects': projects_match.group(1) if projects_match else "Projects not found"
    }

def calculate_fit_score(job_data, resume):
    score = 0

    # Qualification Match
    if resume.get('qualification') and resume['qualification'] != 'Qualification not found':
        if any(q in resume['qualification'] for q in job_data.get('qualification', [])):
            score += 5

    # Primary Skills Matching
    primary_skills = resume.get('primary_skills', [])
    job_primary_skills = job_data.get('primary_skills', [])
    primary_skills_count = sum(skill in primary_skills for skill in job_primary_skills)
    total_primary_skills = len(job_primary_skills)
    
    if total_primary_skills > 0:
        primary_skills_score = (primary_skills_count / total_primary_skills) * 10
        score += primary_skills_score

    # Experience Match
    resume_experience = resume.get('experience', [])
    job_experience = job_data.get('experience', [])
    
    if all(exp >= min_exp for exp, min_exp in zip(resume_experience, job_experience)):
        score += 5

    # Secondary Skills (Bonus)
    secondary_skills = resume.get('secondary_skills', [])
    job_secondary_skills = job_data.get('secondary_skills', [])
    secondary_skills_bonus = sum(skill in secondary_skills for skill in job_secondary_skills) * 3
    score += secondary_skills_bonus

    return score

@app.route('/shortlist', methods=['POST'])
def shortlist_candidates():
    try:
        # Extract job data and resumes from the request
        job_data = request.json.get('job_data', {})
        resumes = request.json.get('resumes', [])
        
        print("Received job data:", job_data)
        print("Received resumes:", resumes)  # Log the resumes for debugging

        # Initialize lists for shortlisted and rejected candidates
        shortlisted = []
        rejected = []
        threshold = 10  # Define your threshold score here

        for resume in resumes:
            print(f"Processing resume: {resume}")  # Debug each resume
            
            # Ensure all required fields are present
            resume['primary_skills'] = resume.get('primary_skills', [])
            resume['experience'] = resume.get('experience', [])
            resume['qualification'] = resume.get('qualification', 'Qualification not found')

            score = calculate_fit_score(job_data, resume)
            rejection_reasons = []
            print(f"Calculated score: {score}")  # Debug the calculated score

            if score >= threshold:
                if resume['qualification'].lower() != "qualification not found" and resume['experience'] and "Skills not found" not in resume.get('skills', []):
                    resume['fit_score'] = score
                    shortlisted.append(resume)
                else:
                    if resume['qualification'].lower() == "qualification not found":
                        rejection_reasons.append("Qualification not found")
                    if not resume['experience']:
                        rejection_reasons.append("Experience not found")
                    if "Primary skills not found" in resume.get('primary_skills', []):
                        rejection_reasons.append("Primary skills not found")

                    rejection_reason = " | ".join(rejection_reasons) if rejection_reasons else "Missing Information"
                    rejected.append({
                        'name': resume['name'],
                        'experience': resume['experience'],
                        'email': resume['email'],
                        'primary_skills': resume['primary_skills'],
                        'qualification': resume['qualification'],
                        'rejection_reason': f"*{rejection_reason}*"
                    })
            else:
                if not resume['experience']:
                    rejection_reasons.append("Experience does not meet the job requirements")
                if resume['qualification'].lower() == "qualification not found":
                    rejection_reasons.append("Qualification does not match the job requirements")
                if "Primary skills not found" in resume.get('primary_skills', []):
                    rejection_reasons.append("Not enough matching primary skills")
                
                rejection_reason = " | ".join(rejection_reasons) if rejection_reasons else "Not matched more than two Job Requirements"
                rejected.append({
                    'name': resume['name'],
                    'experience': resume['experience'],
                    'email': resume['email'],
                    'primary_skills': resume['primary_skills'],
                    'qualification': resume['qualification'],
                    'rejection_reason': f"*{rejection_reason}*"
                })

        # Sort shortlisted candidates by their fit score in descending order
        shortlisted.sort(key=lambda x: x['fit_score'], reverse=True)

        print(f"Shortlisted candidates: {shortlisted}")
        print(f"Rejected candidates: {rejected}")

        # Save the shortlisted and rejected candidates to Excel files
        if shortlisted:
            df_shortlisted = pd.DataFrame(shortlisted)
            df_shortlisted.to_excel(os.path.join('static', 'shortlisted_candidates.xlsx'), index=False)
        if rejected:
            df_rejected = pd.DataFrame(rejected)
            df_rejected.to_excel(os.path.join('static', 'rejected_candidates.xlsx'), index=False)

        # Return the results as JSON
        return jsonify({
            'shortlisted': shortlisted,
            'rejected': rejected
        })

    except Exception as e:
        print(f"Error in shortlist_candidates: {e}")  # Debug statement
        return jsonify({"error": str(e)}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        return send_from_directory('static', filename, as_attachment=True)
    except Exception as e:
        print(f"Error in download_file: {e}")  # Debug statement
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    if not os.path.exists('static'):
        os.makedirs('static')
    app.run(debug=True)