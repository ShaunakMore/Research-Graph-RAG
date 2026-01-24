from retrieval.hybrid import hybrid_content
import google.generativeai as genai
import ollama
import json,os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY")) #type:ignore
model = genai.GenerativeModel("gemini-2.5-flash-lite") #type:ignore

def ask_hybrid(query):
  
  vec_chunks, graph_text, intent = hybrid_content(query)
  
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
  
  res = model.generate_content(
    contents=prompt
  )
  
  try:
    return (res.text)
  except:
    return "Gemini request failed"