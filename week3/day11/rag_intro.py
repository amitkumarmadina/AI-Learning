from asyncio import sleep
import os
import re
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("GROQ_API_KEY not found")

client = Groq(api_key=my_api_key)

model = "groq/compound-mini"


# step 1
knowledge_base = {
    "age" : "The age of amit is 19",
    "net worth" : "networth of amit is 50,000",
    "colour" : "fevroit colour is black"  
}

#step2 retrival
def retriv_info(question):
    question = question.lower()
    if('age' in question):
        return knowledge_base["age"]
    elif('networth' in question):
        return knowledge_base["net worth"]
    elif('colour' in question):
        return knowledge_base["colour"]
    else:
        return None

def askLlm(question):
    context = retriv_info(question)

    sys_prompt = f"""answer in one line and answer only based in {context} dont hallucinate "
    """

    system_message = {
        "role" : "system",
        "content" : sys_prompt
    }
    message = {
        "role" : "user",
        "content" : question
    }
    messsages = [system_message, message]

    response = client.chat.completions.create(
        messages = messsages,
        model = model,
    )     
    answer = response.choices[0].message.content
    return answer

question = "do you know amit kumar madina"


print(askLlm(question))


#uv init dayX
#cd dayx
#uv venv --python 3.11
#.\.venv\Scripts\activate.ps1
#code codes.py
#uv add groq python-dotenv pydantic
#uv add fastapi uvicorn groq python-dotenv pydantic pypdf python-docx
#uv add groq python-dotenv sentence-transformers numpy
#uv add qdrant-client sentence-transformers python-dotenv groq