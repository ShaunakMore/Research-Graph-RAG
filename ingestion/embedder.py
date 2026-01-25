import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

INDEX_NAME = "research-rag"
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

index = pc.Index(INDEX_NAME)

def upload_chunks(chunks, paper_id, user_id):
  # index.delete(delete_all=True,namespace="default")
  # print("Deleted all vectors in namespace")
  
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
  print(f"Uploaded {len(vectors)} chunks for paper ID: {paper_id}")



