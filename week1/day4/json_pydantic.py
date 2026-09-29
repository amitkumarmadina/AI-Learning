import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("GROQ_API_KEY not found")

client = Groq(api_key=my_api_key)

model = "llama-3.1-8b-instant"
role = "user"

#Structuring it
from pydantic import BaseModel
class Ticket(BaseModel):
    name : str
    email : str
    issue : str

schema = Ticket.model_json_schema()
response_formate = {
    "type" : "json_object"
}

system_prompt = f"""
Extract the following information from the customer ticket:

- name
- email
- issue

Return the result strictly as JSON according to this schema:{schema}f"""

message_system = {
    "role": "system",
    "content": system_prompt
}


text = "Hi My name is john. I have purchased a new car. which is not working. My address is delhi. My email is john@gmail.com. My contact number is 12345."
prompt = f"""
this is customer ticket. Please extract the personal information from the text: {text}
f"""

message = {
        "role" : "user",
        "content" : prompt
    }

messages = [message, message_system]

response = client.chat.completions.create(
    model=model,
    messages=messages,
    temperature=0.5,
    response_format=response_formate
)

answer = response.choices[0].message.content
print(answer)


import json
raw_json = answer
data_file = json.loads(raw_json)
ticket = Ticket(**data_file)

print(ticket.name)
print(ticket.issue)

#uv init dayX
#uv venv --python 3.11
#.\.venv\Scripts\activate.ps1
#code codes.py
#uv add groq python-dotenv pydantic
#uv add fastapi uvicorn groq python-dotenv pydantic pypdf python-docx