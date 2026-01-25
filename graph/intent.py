import ollama
import json,os,re
import google.genai as genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY")) 
model_name = os.getenv("GOOGLE_MODEL")

def parse_llm_json(raw_output):
    # Regex to find content between ```json and ```
    match = re.search(r'```json\s+(.*?)\s+```', raw_output, re.DOTALL)
    
    if match:
        clean_json = match.group(1)
    else:
        # Fallback: just strip backticks if it's just ``` ... ```
        clean_json = raw_output.strip().strip('`')
        # If it still has "json" at the start after stripping `
        if clean_json.startswith('json'):
            clean_json = clean_json[4:].strip()

    try:
        return json.loads(clean_json)
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")
        # Log the raw output for debugging
        return  {"type": "general", "paper_ids": [] ,"entities": []}

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
    {paper_list}

    Task: Classify the question and map it to the correct Paper ID if possible.

    Return JSON ONLY:
    {{
      "type": "one of: method | dataset | metric | limitation | claims | general",
      "paper_ids": ["List of the relevant ID from the list above, or null if unknown"],
      "entities": ["list of main subjects explicitly mentioned in the question"]
    }}

    Rules:
    - If the user refers to a paper by title or topic, find the matching ID.
    - DO NOT USE MARKDOWN.
    
    Question: {query}
    """
    res = client.models.generate_content(
    model="gemma-3-27b-it",
    contents=prompt
  )
    try:
        print(f"\nLLM Detected INTENT: {res.text}\n")
        return parse_llm_json(res.text)
    except Exception as e:
        print(e)
        return {"type": "general", "paper_ids": [] ,"entities": []}