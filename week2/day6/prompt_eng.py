import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("GROQ_API_KEY not found")

client = Groq(api_key=my_api_key)

model = "llama-3.1-8b-instant"
def llm_ans(prompt):
    message={
        "role" : "user",
        "content":prompt
    }
    messages = [message]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    ans = response.choices[0].message.content
    return ans


bad_prompt=f"""
#ROLE
You are a support assistant at a mobile/laptop company
#TASK
You have to classify the issue in a category
#CONSTRAINTS
you have to category the issue in one of the following categories: billing, technical, return
#OUTPUT FORMATE
your ans shoukd be one work only and fall under one of the category given 
#EXAMPLE
for instance if a user complain says he wants a refund then the categoru will be Return
#FALLBACK
If the issus is unrelated to the above categories then you will say "unrelated"
This is a user complain:
not happy with laptop
f"""


print(llm_ans(bad_prompt))