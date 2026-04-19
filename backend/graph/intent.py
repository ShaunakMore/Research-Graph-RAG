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
        # Log the raw output for debugging
        return  {"type": "general", "paper_ids": [] ,"entities": []}

def detect_intent(query,paper_list):
    
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
    model=model_name,
    contents=prompt
  )
    try:
        return parse_llm_json(res.text)
    except Exception as e:
        return {"type": "general", "paper_ids": [] ,"entities": []}
