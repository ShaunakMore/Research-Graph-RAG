import ollama
import json
import google.generativeai as genai
from dotenv import load_dotenv

# load_dotenv()
# genai.configure(api_key=os.getenv("GEMINI_API_KEY")) #type:ignore
# model = genai.GenerativeModel("gemini-2.5-flash-lite") #type:ignore


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
    - Strict return VALID JSON ONLY and nothing else ONLY THE JSON
    Question: {query}
    """

    res = ollama.chat(
        model="mistral",
        messages=[{"role": "user", "content": prompt}]
    )
    
    try:
        print(f"\nLLM Detected INTENT: {res["message"]["content"]}\n")
        return json.loads(res["message"]["content"])
    except Exception as e:
        print(e)
        return {"type": "general", "entities": []}