import os
import streamlit as st
import fitz  # PyMuPDF for extracting text from PDFs
import google.generativeai as genai
import re

# Configure Google Gemini API
genai.configure(api_key="AIzaSyB6sis6wxsbnIyKRboG8uRO8g86-aXJKh4")  # Replace with your API key
model = genai.GenerativeModel("gemini-1.5-flash-latest")  # ✅ Faster, but may have lower quality


# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = "\n".join([page.get_text("text") for page in doc])
    return text

# Function to analyze resume with Gemini
def analyze_resume_with_gemini(resume_text, prompt):
    response = model.generate_content([prompt, resume_text])
    return response.text if response else "No response received."

# Function to extract keywords from text
def extract_keywords(text):
    words = re.findall(r'\b\w+\b', text.lower())
    common_keywords = set(words)
    return list(common_keywords)

# Function to score resume based on job description
def score_resume(resume_text, job_description):
    resume_words = set(resume_text.lower().split())
    job_words = set(job_description.lower().split())
    match_score = len(resume_words & job_words) / len(job_words) * 100 if job_words else 0
    return round(match_score, 2)

# Streamlit UI
st.title("Resume ATS with Google Gemini Pro")

# Upload PDF file
uploaded_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"])

# Field to input Job Description
job_description = st.text_area("Enter Job Description")

# Prompt Template Selection
prompt_templates = {
    "Basic Analysis": "Extract key skills and experience from this resume.",
    "JD Match": "Compare the resume with this job description: " + job_description,
    "Red Flags": "Identify potential red flags in this resume."
}
prompt_choice = st.selectbox("Select Prompt", list(prompt_templates.keys()))

if uploaded_file:
    # Save PDF temporarily
    pdf_path = "temp_resume.pdf"
    with open(pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Extract text from PDF
    resume_text = extract_text_from_pdf(pdf_path)
    
    # Process resume with Gemini
    selected_prompt = prompt_templates[prompt_choice]
    analysis_result = analyze_resume_with_gemini(resume_text, selected_prompt)
    
    # Extract keywords
    keywords = extract_keywords(resume_text)
    
    # Score Resume Match
    match_score = score_resume(resume_text, job_description)
    
    # Display results
    st.subheader("Analysis Result")
    st.write(analysis_result)
    
    st.subheader("Extracted Keywords")
    st.write(", ".join(keywords))
    
    st.subheader("Resume Match Score")
    st.write(f"{match_score}% match with job description")
    
    # Cleanup
    os.remove(pdf_path)