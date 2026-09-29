from langchain_text_splitters import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter
)


text = """
The deactivate entered the abandoned house just befoore midnight. 
The silence in the hallway was heavy and thick, broken only by the sound of his own breathing and the creak of old floorboards underfoot.
He checked his watch; the luminous hands glowed with a faint, eerie green light, telling him he had less than ten minutes to complete the mission before the extraction team arrived.
Outside, a storm was brewing, its first drops of rain tapping against the grimy windows like skeletal fingers.
"""

fixed = CharacterTextSplitter(
    separator = "",
    chunk_size = 100,
    chunk_overlap = 20,
)

print("\n == FIXED SIZE == ")
for i, chunk in enumerate(fixed.split_text(text), 1):
    print(f"Chunk {i} : ")
    print(chunk)
    print("-----------")

# 2. PARAGRAPH CHUNKING

paragraph = CharacterTextSplitter(
    separator = "\n\n",
    chunk_size = 100,
    chunk_overlap = 0,
)

print("\n == PARAGRAPH CHUNKING == ")

for i, chunk in enumerate(paragraph.split_text(text), 1):
    print(f"\nChunk {i} : ")
    print(chunk)
    print("-----------")

#Recursive chunking

recursive = RecursiveCharacterTextSplitter(
    chunk_size = 100,
    chunk_overlap = 20
)
print("\n == RECURSIVE CHUNKING == ")

for i, chunk in enumerate(recursive.split_text(text), 1):
    print(f"\nChunk {i} : ")
    print(chunk)
    print("-----------")


#uv init dayX
#cd dayx
#uv venv --python 3.11
#.\.venv\Scripts\activate.ps1
#code codes.py
#uv add groq python-dotenv pydantic
#uv add fastapi uvicorn groq python-dotenv pydantic pypdf python-docx
#uv add groq python-dotenv sentence-transformers numpy
#uv add qdrant-client sentence-transformers python-dotenv groq