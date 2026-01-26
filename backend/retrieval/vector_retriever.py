from pinecone import Pinecone
import os
from dotenv import load_dotenv

load_dotenv()

INDEX_NAME = os.getenv("INDEX_NAME")
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

index = pc.Index("research-rag")

def retrieve_chunks(query,paper,user_id,top_k=3):
    results = []
    if paper:   
        results = index.search(
            namespace=user_id,
            query={                   #type:ignore
                "top_k": top_k,
                "inputs": {
                    'text': query
                },
                "filter": {"paper":{"$eq": f"{paper}"}}  
            }
            )
    else:
        results = index.search(
            namespace=user_id,
            query={                   #type:ignore
                "top_k": top_k,
                "inputs": {
                    'text': query
                } 
            }
            )
      
    return [f"[CTX_{i+1}]{match['fields']['text']}" for i,match in enumerate(results["result"]['hits'])]