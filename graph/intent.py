import ollama
import json
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY")) #type:ignore
model = genai.GenerativeModel("gemini-2.5-flash-lite") #type:ignore


def detect_intent(query):

    prompt = f"""
    Classify the research question.

    Return JSON ONLY in this format:

    {{
      "type": "one of: method | dataset | metric | limitation | claims | general",
      "entities": ["list of main subjects explicitly mentioned in the question"]}}

    Rules:
    - entities must be an ARRAY
    - include all relevant subjects (e.g. BERT, GPT, ResNet)
    - if no clear subject exists, return an empty array []
    - do not include explanations
    - DONT USE MARKDOWN FORMAT.
    Question: {query}
    """

    # res = ollama.chat(
    #     model="mistral",
    #     messages=[{"role": "user", "content": prompt}]
    # )
    res = model.generate_content(
    contents=prompt
  )
  
    try:
        print(f"\nLLM Detected INTENT: {res.text}\n")
        return json.loads(res.text)
    except Exception as e:
        print(e)
        return {"type": "general", "entities": []}