import ollama
import json,os
import google.genai as genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY")) 
model_name = os.getenv("GOOGLE_MODEL")

def detect_intent(query,paper_list):

    # prompt = f"""
    # Classify the research question.

    # Return JSON ONLY in this format:

    # {{
    #   "type": "one of: method | dataset | metric | limitation | claims | general",
    #   "entities": ["list of main subjects explicitly mentioned in the question"]}}

    # Rules:
    # - entities must be an ARRAY
    # - include all relevant subjects (e.g. BERT, GPT, ResNet)
    # - if no clear subject exists, return an empty array []
    # - do not include explanations 
    # - DO NOT USE MARKDOWN FORMAT like ```json ```
    # Question: {query}
    
    # - DO NOT USE MARKDOWN FORMAT
    # """

    # res = ollama.chat(
    #     model="mistral",
    #     messages=[{"role": "user", "content": prompt}]
    # )
    
    prompt = f"""
    You are an intent classifier for a Research Assistant.
    Available Papers:
    {json.dumps(paper_list, indent=2)}

    Task: Classify the question and map it to the correct Paper ID if possible.

    Return JSON ONLY:
    {{
      "type": "method | dataset | metric | limitation | claims | general",
      "paper_id": "The ID from the list above, or null if unknown",
      "entities": ["list of entities"]
    }}

    Rules:
    - If the user refers to a paper by title or topic, find the matching ID.
    - Entities should be the specific methods or subjects (e.g., "Transformer").
    - DO NOT USE MARKDOWN.
    
    Question: {query}
    """
    res = client.models.generate_content(
    model="gemma-3-27b-it",
    contents=prompt
  )
    try:
        print(f"\nLLM Detected INTENT: {res.text}\n")
        return json.loads(res.text)
    except Exception as e:
        print(e)
        return {"type": "general", "entities": []}