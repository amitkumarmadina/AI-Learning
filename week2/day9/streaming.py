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

prompt = "explain me how internet works"
message = {
    "role" : "system",
    "content" : prompt
}
messages = [message]
#response1 = client.chat.completions.create(model = model,messages = messages)
#print(response1)
#answer = response1.choices[0].message.content
#print(answer)

stream = client.chat.completions.create(model = model,messages = messages, stream = True)
for chunk in stream:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end = "", flush = True)
