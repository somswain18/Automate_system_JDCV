import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from agents.parser import extract_text_from_pdf, extract_text_from_docx

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def get_text_from_file(filepath):
    ext = filepath.split('.')[-1].lower()
    text = ''
    if ext == 'pdf':
        text = extract_text_from_pdf(filepath)
    elif ext == 'docx':
        text = extract_text_from_docx(filepath)
    elif ext == 'txt':
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        raise ValueError(f"Unsupported file type: {ext}. Please use PDF, DOCX, or TXT files.")
    return clean_text(text)

def calculate_jd_cv_match(jd_text, cv_text):
    vectorizer = TfidfVectorizer()
    if not jd_text.strip() or not cv_text.strip():
        return 0.0
    vectors = vectorizer.fit_transform([jd_text, cv_text])
    score = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
    return round(score * 100, 2)

def match_jd_cv(jd_file, cv_file):
    jd_text = get_text_from_file(jd_file)
    cv_text = get_text_from_file(cv_file)
    return calculate_jd_cv_match(jd_text, cv_text)

# import re
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity

# def clean_text(text):
#     """
#     Clean the input text by converting it to lowercase and removing special characters.
#     """
#     text = text.lower()
#     text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)  # Remove special characters
#     text = re.sub(r'\s+', ' ', text)  # Remove extra spaces
#     return text.strip()

# def get_text_from_file(filepath):
#     """
#     Get cleaned text from a given file (PDF, DOCX, TXT).
#     """
#     ext = filepath.split('.')[-1]
#     text = ''
#     if ext == 'pdf':
#         from agents.parser import extract_text_from_pdf
#         text = extract_text_from_pdf(filepath)
#     elif ext == 'docx':
#         from agents.parser import extract_text_from_docx
#         text = extract_text_from_docx(filepath)
#     elif ext == 'txt':
#         with open(filepath, 'r', encoding='utf-8') as f:
#             text = f.read()
#     return clean_text(text)

# def calculate_jd_cv_match(jd_text, cv_text):
#     """
#     Calculate the match score between Job Description (JD) and CV based on cosine similarity.
#     """
#     vectorizer = TfidfVectorizer()  # Convert text into vectors using TF-IDF
#     vectors = vectorizer.fit_transform([jd_text, cv_text])  # Fit and transform the text into vectors
#     score = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]  # Calculate cosine similarity
#     return round(score * 100, 2)  # Convert to percentage

# def match_jd_cv(jd_file, cv_file):
#     """
#     Main function to process JD and CV files and calculate the match score.
#     """
#     # Extract text from JD and CV
#     jd_text = get_text_from_file(jd_file)
#     cv_text = get_text_from_file(cv_file)

#     # Calculate match score between JD and CV
#     match_score = calculate_jd_cv_match(jd_text, cv_text)

#     return match_score

# # Example usage
# jd_file = "/home/som/Documents/automated_cv_system/job_descriptions/Elint_jd.pdf"  # Replace with actual JD file path
# cv_file = "/home/som/Documents/automated_cv_system/resumes"  # Replace with actual CV file path

# match_score = match_jd_cv(jd_file, cv_file)
# print(f"The JD-CV match score is: {match_score}%")
