import PyPDF2
import docx
import re

# Define a more comprehensive list of skills
skills_list = [
    "Python", "JavaScript", "React", "Machine Learning", "Java", "SQL", "HTML", "CSS", "MySQL",
    "ROS", "C", "C++", "R", "Creativity", "Docker", "Kubernetes", "Git", "AWS", "Azure", "GCP",
    "Node.js", "TypeScript", "Scala", "Hadoop", "Spark", "TensorFlow", "PyTorch", "Swift", "Kotlin",
    "PHP", "Ruby", "Perl", "Excel", "Power BI", "Tableau", "Go", "Rust", "Jupyter", "NumPy", "Pandas",
    "Matplotlib", "Seaborn", "OpenCV", "NLTK", "SpaCy", "FastAPI", "Flask", "Django"
]

def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ''
    for page in pdf_reader.pages:
        text += page.extract_text() or ''
    return text

def read_docx(file):
    doc = docx.Document(file)
    text = ''
    for para in doc.paragraphs:
        text += para.text + '\n'
    return text

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

def extract_experience(resume_text):
    experience_pattern = r'(\d+\s*years? experience|\bexperience\b)'
    experiences = re.findall(experience_pattern, resume_text, re.IGNORECASE)
    return experiences[0] if experiences else "Experience not found"

def extract_skills(resume_text):
    resume_text_lower = resume_text.lower()
    extracted_skills = []
    for skill in skills_list:
        pattern = re.compile(r'\b' + re.escape(skill.lower()) + r'\b', re.IGNORECASE)
        if pattern.search(resume_text_lower):
            extracted_skills.append(skill)
    return extracted_skills if extracted_skills else "Skills not found"

def parse_resume(resume_text):
    name = extract_name(resume_text)
    email = extract_email(resume_text)
    experience = extract_experience(resume_text)
    skills = extract_skills(resume_text)
    
    if not isinstance(skills, list):
        skills = []

    return {
        'name': name,
        'email': email,
        'experience': experience,
        'skills': skills
    }

def parse_job_description(file):
    # Placeholder function - implement parsing logic for job descriptions
    # Replace this with actual parsing code
    text = ''
    if file.filename.lower().endswith('.pdf'):
        text = read_pdf(file)
    elif file.filename.lower().endswith('.docx'):
        text = read_docx(file)
    elif file.filename.lower().endswith('.txt'):
        text = file.read().decode('utf-8')
    
    # Example parsing - replace with actual logic
    job_data = {
        'skills': extract_skills(text),
        'experience': extract_experience(text),
        'qualifications': 'Qualifications extraction logic here'
    }
    
    return job_data

def calculate_fit_score(job_data, resume):
    # Implement your matching logic here
    score = 0
    # Example scoring logic
    if resume['skills'] and set(job_data['skills']).intersection(resume['skills']):
        score += 10
    if job_data['experience'] in resume['experience']:
        score += 5
    return score

def allowed_file(filename):
    allowed_extensions = {'pdf', 'docx', 'txt'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
