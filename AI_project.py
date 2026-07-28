from fastapi import FastAPI, UploadFile, Form
from pypdf import PdfReader
import io
import re
import math
from collections import Counter

app = FastAPI()

def get_word_counts(text):
    words = re.findall(r'\w+', text.lower())
    return Counter(words)

def cosine_similarity_manual(text1, text2):
    counts1 = get_word_counts(text1)
    counts2 = get_word_counts(text2)
    all_words = set(counts1.keys()) | set(counts2.keys())

    dot_product = sum(counts1.get(word, 0) * counts2.get(word, 0) for word in all_words)
    magnitude1 = math.sqrt(sum(v**2 for v in counts1.values()))
    magnitude2 = math.sqrt(sum(v**2 for v in counts2.values()))

    if magnitude1 == 0 or magnitude2 == 0:
        return 0
    return dot_product / (magnitude1 * magnitude2)

@app.post("/screen-file")
async def screen_resume_file(file: UploadFile, job_description: str = Form(...), required_skills: str = Form(...)):
    contents = await file.read()
    pdf_reader = PdfReader(io.BytesIO(contents))

    extracted_text = ""
    for page in pdf_reader.pages:
        extracted_text += page.extract_text()

    resume_text = re.sub(r'(?<=\w) (?=\w)', '', extracted_text)

    similarity = cosine_similarity_manual(resume_text, job_description)

    skills_list = required_skills.split(",")
    missing_skills = []
    for skill in skills_list:
        skill = skill.strip()
        if skill.lower() not in resume_text.lower():
            missing_skills.append(skill)

    return {
        "match_score": round(similarity, 2),
        "missing_skills": missing_skills
    }