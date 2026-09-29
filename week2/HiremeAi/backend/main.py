import json
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel, Field
from pypdf import PdfReader

load_dotenv()
client = Groq(
    api_key = os.getenv("GROQ_API_KEY")
)

model = "groq/compound-mini"

app = FastAPI(title="HiremeAi Candidate API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Experience(BaseModel):
    company: str | None = None
    role: str | None = None
    duration: str | None = None
    description: str | None = None
    skills_used: list[str] = Field(default_factory=list)

class Education(BaseModel):
    school_name: str | None = None
    graduation: str | None = None

class Project(BaseModel):
    name: str | None = None
    start_date: str | None = None

class Resume(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    total_experience_years: float | None = None
    skills: list[str] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)

cached_resume: Resume | None = None

def read_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

resume_schema = Resume.model_json_schema()

class ChatQuestion(BaseModel):
    question: str

def ask_candidate_stream(question: str, resume: Resume):
    system_prompt = f"""
You are an AI assistant representing a job candidate.

Below is everything you know about the candidate.

{resume.model_dump_json(indent=2)}

Rules:
1. Answer only using this information.
2. Never hallucinate.
3. If information is unavailable, say "I don't have enough information to answer that."
4. Answer concisely and professionally as if HR is interviewing this candidate.
"""

    def event_generator():
        stream = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            stream=True
        )
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content

    return StreamingResponse(event_generator(), media_type="text/plain")

def parse_resume(resume_text):
    system_prompt = f"""
You are an expert resume parser.

Extract information from the resume based on its meaning,
not only based on exact section headings.

Return ONLY valid JSON matching this schema:

{resume_schema}

IMPORTANT RULES:
1. Do not invent information.
2. If a single value is not available, return null.
3. If a list has no information, return [].
4. Include internships inside the experience list.
5. Extract skills mentioned across the entire resume.
6. Education MUST be an array of objects with school_name and graduation.
7. Projects MUST be an array of objects with name and start_date.
8. Experience MUST be an array of objects with company, role, duration, description, skills_used.
9. total_experience_years must be a number.
10. Return the actual extracted resume data."""

    user_prompt = f"Parse the following resume:\n\n{resume_text}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={"type": "json_object"}
    )

    raw_output = response.choices[0].message.content
    if not raw_output:
        raise ValueError("LLM returned an empty resume response")

    data = json.loads(raw_output)
    print("\n========== RESUME DATA ==========")
    print(data)
    print("=================================")

    return Resume(**data)

def get_cached_resume() -> Resume:
    global cached_resume
    if cached_resume is None:
        pdf_path = Path("my_resume.pdf")
        if not pdf_path.exists():
            pdf_path = Path(__file__).parent / "my_resume.pdf"
        resume_text = read_pdf(pdf_path)
        cached_resume = parse_resume(resume_text)
    return cached_resume

@app.get("/")
def home():
    resume = get_cached_resume()
    return {
        "message": "RESUME PARSED!",
        "candidate_name": resume.name
    }

@app.get("/candidate")
def get_candidate():
    resume = get_cached_resume()
    return resume.model_dump()

@app.post("/chat")
def chat(request: ChatQuestion):
    resume = get_cached_resume()
    return ask_candidate_stream(question=request.question, resume=resume)

