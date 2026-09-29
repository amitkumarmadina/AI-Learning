import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from groq import Groq
from sentence_transformers import SentenceTransformer

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).parent.resolve()
load_dotenv(BASE_DIR / ".env")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)
print("Connected to Qdrant Successfully")

COLLECTION_NAME = "knowledge"
EMBEDDING_SIZE = 384

if client.collection_exists(COLLECTION_NAME):
    print(f"Deleting existing collection: {COLLECTION_NAME}")
    client.delete_collection(COLLECTION_NAME)

client.create_collection(
    collection_name = COLLECTION_NAME,
    vectors_config = VectorParams(
        size = EMBEDDING_SIZE,
        distance = Distance.COSINE,
    ),
)


print(f"Created Collection : {COLLECTION_NAME}")
print(f"Vector size : {EMBEDDING_SIZE}")
print("Distance : COSINE")

#PART 4
with open(BASE_DIR / "knowlwdge.txt", "r", encoding = "utf-8") as f:
    documents = [
        line.strip()
        for line in f 
        if line.strip()
    ]

print(f"Loading {len(documents)} documents")

#part 5

print("Loading groq Embedding Model...")
model  = SentenceTransformer('all-MiniLM-L6-v2')

print("Embedding Model Loaded Successfully")

embeddings = model.encode(documents)

print(f"Generated {len(embeddings)} embeddings")
print(f"Embedding size : {len(embeddings[0])}")

#part 6

points = []

for i, embedding in enumerate(embeddings):
    point = PointStruct(
        id = i + 1,
        vector = embedding.tolist(),
        payload = {
            "text" : documents[i]
        }
    )
    points.append(point)

print("Points Created Successfully")

#part 7
client.upsert(
    collection_name = COLLECTION_NAME,
    points = points
)

print(f"Uploaded {len(points)} documents to Qdrant!")

#part 8

def search(query, top_k = 3):
    query_vector = model.encode(query).tolist()
    results = client.query_points(
        collection_name = COLLECTION_NAME,
        query = query_vector,
        limit = top_k,
        with_payload = True
    ).points
    return results

#part 9

query = "How many vacation day do I get?"
results = search(query, top_k = 3)
print("\nSearch results:")

for result in results:
    print(f"Score : {result.score}")
    print(result.payload["text"])
    print()

#part 10

groq_client = Groq(
    api_key = GROQ_API_KEY
)

#part 11

def ask_llm(question, context):
    prompt = f"""
    Answer the question using only the information given below
    Context : {context}

    Question : {question}
    If the answer is not present in the context, say:
    "I dont know based on the provided information."
    """
    response = groq_client.chat.completions.create(
            model = "openai/gpt-oss-120b",
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
    return response.choices[0].message.content
    
    
#part 12

question = "How many vacation days do I get?"
results = search(question, top_k = 3)
context = "\n".join(
    result.payload["text"]
    for result in results
)

answer = ask_llm(question, context)
print("\nFinal Answer:")
print(answer)
