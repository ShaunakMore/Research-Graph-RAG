from retrieval.hybrid import hybrid_content
import google.genai as genai
import ollama
import json,os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY")) 
model_name = os.getenv("GOOGLE_MODEL")

def ask_hybrid(query,paper_list,user_id):
  
  vec_chunks, graph_text, _ = hybrid_content(query,paper_list,user_id=user_id)
  
  context = "\n\n".join(vec_chunks)
  
  print(f"\n\nGraph returns = {graph_text}\n\n")
  prompt = f"""
  You are a research assistant. You answer question on papers based on the provided context.
  Provided context has 2 parts text context and graph facts.
  You should not answer the query using external knowledge other than the provided context.
  
  RULES:
  - You answer the query asked ONLY based on the graph facts and the text context provided.
  - DO NOT ANSWER USING EXTERNAL KNOWLEDGE.
  - GIVE AS MUCH RELEVANT INFORMATION ABOUT THE QUERY ASKED AS POSSIBLE ONLY FROM THE CONTEXT PROVIDED
  - Every factual claim MUST include a citation. Use [CTX_n] for text citation and [GRAPH_n] for graph facts citation.
  - If unsure, say you don't know.
    
  TEXT CONTEXT:
  {context}
  
  GRAPH FACTS:
  {graph_text}
  
  QUESTION:
  {query}
  
  """
  
  # res = ollama.chat(
  #   model = "mistral",
  #   messages=[{"role":"user","content":prompt}]
  # )
  
  # return res["message"]["content"]
  
  res = client.models.generate_content(
    model="gemma-3-27b-it",
    contents=prompt
  )
  
  try:
    return (res.text)
  except:
    return "Gemini request failed"