from asyncio import sleep
import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
import numpy as np
from sentence_transformers import SentenceTransformer

load_dotenv()
my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("Groq API Key not found")

groq_client = Groq(api_key=my_api_key)

model = SentenceTransformer('all-MiniLM-L6-v2') 
groqmodel = "openai/gpt-oss-20b"

documents = [
    "Employees receive 24 days of paid leave per year.",

    "Employees work from the office on Tuesday, Wednesday and Thursday. "
    "Monday and Friday are optional work-from-home days.",

    "Employees receive Rs 3000 per month for gym reimbursement.",

    "Employees can claim Rs 2000 per month for home internet.",

    "Employees have a 90 day notice period."
]

documents_embeddings = model.encode(documents)

def cosine_similarity(a,b):
    return np.dot(a,b) / (
        np.linalg.norm(a) * np.linalg.norm(b)
        )

def retrive(qembedding):
    scores = []
    for i, document in enumerate(documents_embeddings):
        score = cosine_similarity(qembedding,document)
        scores.append((score, documents[i]))
    scores.sort(reverse=True)
    return scores[0]

def askLlm(question, context):
    sys_prompt = (
        f"Answer in one line using only this context: {context}. "
        "Do not hallucinate."
    )

    system_message = {
        "role" : "system",
        "content" : sys_prompt
    }
    message = {
        "role" : "user",
        "content" : question
    }
    messsages = [system_message, message]

    response = groq_client.chat.completions.create(
        messages = messsages,
        model = groqmodel,
    )     
    answer = response.choices[0].message.content
    return answer



query = "How much vacations do I get?"
qembedding = model.encode(query)
score,context = retrive(qembedding)

answer = askLlm(query, context)
print(answer)