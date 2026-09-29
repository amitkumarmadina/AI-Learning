from asyncio import sleep
import os
import re
import time
from dotenv import load_dotenv
from groq import Groq
load_dotenv()

my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("GROQ_API_KEY not found")

client = Groq(api_key=my_api_key)

model = "llama-3.1-8b-instant"

JD = f"""
We are hiring a Backend Python Developer.

Requirements:

Strong Python
FastAPI or Django
PostgreSQL
Docker
AWS
REST APIs
2+ years of experience
f"""
RESUME = f"""
Name: Rahul Sharma

Experience:
3 years as a Software Developer.

Skills:
Python, FastAPI, MySQL, Docker, REST APIs, Git

Projects:
Built a food delivery backend using FastAPI and MySQL.

Deployed applications using Docker.
"""

def ask_llm(system_prompt, user_prompt):
    sys_msg = {
        "role" : "system",
        "content" : system_prompt
    }
    user_msg = {
        "role" : "user",
        "content" : user_prompt
    }
    messages = [sys_msg, user_msg]
    response = client.chat.completions.create(
        model = model,
        messages = messages
    )
    answer = response.choices[0].message.content
    return answer

def step1_res_extract():
    system_prompt = f"""
    You are a professional HR assistant. Extract the skills from the candidates resume provided.Only return the skills only Strictly no other information
    Do not invent any skills by yourself.
    """
    user_prompt = f"""
    Extract the skills form this resume:
    {RESUME}
    """
    return ask_llm(system_prompt, user_prompt)

def step2_JD_extract():
    system_prompt = f"""
    You are a professional HR assistant. Extract the skills from the job description provided.Only return the skills only Strictly no other information
    Do not invent any skills by yourself.
    """
    user_prompt = f"""
    Expract the skills form this  job description
    {JD}
    """
    return ask_llm(system_prompt, user_prompt)

def step3_match(candidate, jd):
    system_prompt = f"""
    You are a professional HR assistant. compare the skills of candidate and the skilles required in jd and produce a final sccore form 1 to 100 and also providea shoort verdic whather the candidate is fit for the role or not
    """
    user_prompt = f"""
   compare and match the skills
   JD:
   {jd}
   candidate:
   {candidate}
    """
    return ask_llm(system_prompt, user_prompt)

candidate = step1_res_extract()
time.sleep(2)
jd = step2_JD_extract()
sleep(2)
score = step3_match(candidate,jd)
sleep(2)
print(score)