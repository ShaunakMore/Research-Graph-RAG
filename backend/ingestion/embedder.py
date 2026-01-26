import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

INDEX_NAME = os.getenv("INDEX_NAME")
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

index = pc.Index("research-rag")

def upload_chunks(chunks, paper_id, user_id):
  vectors = []
  for i, chunk in enumerate(chunks):
    if len(vectors)<96:
      vectors.append({
        "id": f"{paper_id}_{i}",
        "text": chunk["text"],
        "paper": paper_id,
        "section": chunk["section"]
      })
    else:
      index.upsert_records(namespace=user_id,records=vectors)
      vectors = []
  
  if vectors:
    index.upsert_records(namespace=user_id,records=vectors)



