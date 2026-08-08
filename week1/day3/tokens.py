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

# 3 prompts 
prompt1 = "Hi!"
prompt2 = "Explian BLACK HOLE iin details"
prompt3 = "Write 500 words essay on the impact of climate change on agriculture"
prompts = [prompt1, prompt2, prompt3]


for prompt in prompts:
    message = {
        "role" : "user",
        "content" : prompt
    }

    messages = [message]

    response = client.chat.completions.create(
    model=model,
    messages=messages,
    max_tokens=5000,
)

    usage = response.usage
    print(f"Prompt :{prompt} --> ypur_tokens : {usage.prompt_tokens} completion_tokens : {usage.completion_tokens} total_tokens : {usage.total_tokens} Finish Reason : {response.choices[0].finish_reason}")


# message_sys = {
#     "role": "system",
#     "content": "You are a brand manager who suggest name for my new company"
# }
# message = {
#         "role" : "user",
#         "content" : prompt
#     }

# messages = [message_sys, message]


# response = client.chat.completions.create(
#     model=model,
#     messages=messages,
#     temperature=2,
    
# )

# print(response.choices[0].message.content)
