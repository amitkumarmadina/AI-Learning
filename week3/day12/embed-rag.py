from asyncio import sleep
import os
import re
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer 
import numpy as np

def cosine_similarity(a,b):
    return np.dot(a,b) / (
        np.linalg.norm(a) * np.linalg.norm(b)
        )
    
model = SentenceTransformer('all-MiniLM-L6-v2') 
text = "Machine learning is fun"

#embedding = model.encode(text)
#print(embedding.shape)
#print(embedding)

t1 = "There are 24 piad leaves"
t2 = "There are 24 vacation days"

v1 = model.encode(t1)
v2 = model.encode(t2)
print(cosine_similarity(v1, v2))