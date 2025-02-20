from flask import Flask, request, jsonify
from flask_cors import CORS
import spacy
import re
import PyPDF2
import docx
import re
from sklearn.feature_extraction.text import TfidfVectorizer

# Load spaCy model for Named Entity Recognition (NER)
nlp = spacy.load("en_core_web_md")

# Define soft skills manually (no nltk needed)
SOFT_SKILLS = {"communication", "leadership", "collaboration", "problem-solving", "teamwork"}

# Define a simple set of stopwords (to avoid nltk)
STOPWORDS = {"the", "and", "is", "in", "to", "of", "for", "on", "with", "at", "by", "a", "an", "be", "this", "it", "that", "as"}

# Define common technical skills manually (replaces nltk-based keyword extraction)
TECHNICAL_TERMS = {"python", "java", "c++", "golang", "tensorflow", "pytorch", "scikit-learn", "deep learning", 
                   "machine learning", "nlp", "computer vision", "aws", "gcp", "azure", "docker", "kubernetes", 
                   "flask", "django", "sql", "nosql", "mongodb", "postgresql", "big data", "hadoop", "spark",
                   "api", "microservices", "data engineering", "data pipelines", "cloud computing"}

app = Flask(__name__)
CORS(app)

# Function to extract text from a DOCX file
def extract_text_from_docx(file):
    """Extracts text from a DOCX file object."""
    try:
        document = docx.Document(file)
        return "\n".join([para.text for para in document.paragraphs])
    except Exception as e:
        return str(e)

# Function to extract text from a PDF file
def extract_text_from_pdf(file):
    """Extracts text from a PDF file object."""
    try:
        reader = PyPDF2.PdfReader(file)
        text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
        return text if text else "Unable to extract text from PDF."
    except Exception as e:
        return str(e)

# Function to extract relevant skills from text
def extract_skills_from_text(text):
    """Extracts relevant technical skills from job description using Named Entity Recognition (NER) and filtering."""
    doc = nlp(text)
    skills = set()

    TECHNICAL_TERMS = {
        "python", "java", "c++", "golang", "tensorflow", "pytorch", "scikit-learn", "deep learning", 
        "machine learning", "nlp", "computer vision", "aws", "gcp", "azure", "docker", "kubernetes", 
        "flask", "django", "sql", "nosql", "mongodb", "postgresql", "big data", "hadoop", "spark",
        "api", "microservices", "data engineering", "data pipelines", "cloud computing", "react", "node.js"
    }

    for token in doc:
        word = token.text.lower()
        if word in TECHNICAL_TERMS:
            skills.add(word)

    return skills



# Function to compute similarity using TF-IDF
def calculate_tfidf_similarity(job_desc, resume_text):
    """Computes similarity between job description and resume using TF-IDF."""
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([job_desc, resume_text])
    similarity = (vectors * vectors.T).toarray()[0, 1]
    return round(similarity * 100, 2)  # Convert to percentage

# Function to calculate hybrid similarity (TF-IDF + spaCy)
def calculate_hybrid_similarity(job_desc, resume_text):
    """Computes similarity using a combination of TF-IDF and spaCy word embeddings."""
    tfidf_score = calculate_tfidf_similarity(job_desc, resume_text)
    job_desc_doc = nlp(job_desc)
    resume_doc = nlp(resume_text)
    spacy_score = job_desc_doc.similarity(resume_doc) * 100  # Convert to percentage

    # Weighted combination
    final_score = (tfidf_score * 0.5) + (spacy_score * 0.5)
    return round(final_score, 2)

# Function to generate personalized resume improvement suggestions
def generate_resume_suggestions(job_desc, resume_text):
    suggestions = []

    # Extract important words from job description and resume
    job_keywords = set(job_desc.lower().split())
    resume_keywords = set(resume_text.lower().split())

    # Check for missing technical skills
    missing_skills = job_keywords - resume_keywords
    if missing_skills:
        suggestions.append(f"You may want to highlight skills like: {', '.join(list(missing_skills)[:5])}.")

    # Check if resume already has quantifiable results
    quantifiable_patterns = [
        r"\b\d+%\b",  # Percentage improvements (e.g., "Reduced costs by 30%")
        r"\b\d+\+\b",  # Large numbers (e.g., "Managed 10+ projects")
        r"\b(increased|decreased|improved|optimized|growth|reduced|saved)\b"
    ]
    
    has_quantifiable_results = any(re.search(pattern, resume_text.lower()) for pattern in quantifiable_patterns)
    
    if not has_quantifiable_results:
        suggestions.append("Consider adding **quantifiable results**, such as 'Reduced migration time by 40%' or 'Optimized data processing by 25%'.")

    # Check for soft skills
    soft_skills = ["leadership", "collaboration", "communication", "teamwork", "problem-solving"]
    missing_soft_skills = [skill for skill in soft_skills if skill not in resume_keywords]
    if missing_soft_skills:
        suggestions.append(f"Consider mentioning soft skills like {', '.join(missing_soft_skills)} to strengthen your resume.")

    return suggestions


# Flask route to handle file uploads
@app.route("/upload", methods=["POST"])
def upload():
    """Handles file uploads and provides resume improvement suggestions."""
    try:
        print("📥 Request Received")
        print("➡ Form Data:", request.form)
        print("➡ Files Received:", request.files)

        if "job_desc" not in request.form:
            return jsonify({"error": "Job description is missing"}), 400
        
        if "resume" not in request.files:
            return jsonify({"error": "Resume file is missing"}), 400

        job_desc = request.form["job_desc"]
        file = request.files["resume"]

        print("✅ Job Description:", job_desc)
        print("✅ Resume File Name:", file.filename)

        file_ext = file.filename.split(".")[-1].lower()
        if file_ext not in {"pdf", "docx"}:
            return jsonify({"error": "Unsupported file format"}), 400

        # Extract resume text
        resume_text = extract_text_from_pdf(file) if file_ext == "pdf" else extract_text_from_docx(file)
        if not resume_text.strip():
            return jsonify({"error": "Could not extract text from the resume"}), 400

        # Compute compatibility score
        match_score = calculate_hybrid_similarity(job_desc, resume_text)

        # Generate actionable resume improvement suggestions
        suggestions = generate_resume_suggestions(job_desc, resume_text)

        print("✅ Match Score:", match_score)
        print("✅ Suggestions:", suggestions)

        return jsonify({"match_score": match_score, "suggestions": suggestions})

    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
