import google.genai as genai
import os
from dotenv import load_dotenv
import json
import re

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
        return {
          "methods": [],
          "datasets": [],
          "metrics": [],
          "limitations": [],
          "claims": []
        }

def extract_entities(section, paper_name, text):
  SCHEMA = f"""
      # ROLE
    You are a Senior Research Scientist specializing in Knowledge Graph Construction. Your task is to extract high-fidelity entities and relationships from a research paper to populate a GraphRAG database.

    # CONTEXT
    - **Paper Title:** {{paper_title}}
    - **Current Section:** {{section_name}}
    - **Text Chunk:** {{chunk_text}}

    # EXTRACTION TAXONOMY & RULES

    ### 1. METHODS (The "How")
    - **INCLUDE:** Specific named architectures (e.g., "ResNet-50"), algorithms (e.g., "Backpropagation"), or novel frameworks introduced by the authors.
    - **STATUS CHECK:** You MUST distinguish between 'PROPOSED' (the authors created it) and 'BASELINE' (the authors are just using/comparing it).
    - **EXCLUDE:** General concepts (e.g., "Artificial Intelligence"), software libraries (e.g., "PyTorch"), or hardware (e.g., "NVIDIA H100").

    ### 2. DATASETS (The "Where")
    - **INCLUDE:** Public benchmarks (e.g., "SQuAD v2.0"), private corpora, or simulated environments.
    - **RELATIONSHIP:** Identify which specific METHOD was evaluated on this dataset.
    - **EXCLUDE:** File extensions, general descriptions like "the web," or sample sizes (e.g., "100 images") unless they have a proper name.

    ### 3. METRICS (The "Success")
    - **INCLUDE:** Specific evaluative measures (e.g., "F1-Score," "Precision," "Latency (ms)").
    - **RELATIONSHIP:** Identify which METHOD this metric is measuring.
    - **EXCLUDE:** Raw numerical results (e.g., "94%"), training hyperparameters (e.g., "learning rate"), or non-evaluative statistics.

    ### 4. CLAIMS (The "Value")
    - **INCLUDE:** High-level factual findings (e.g., "Our model outperforms Transformer-X by 15% in low-resource settings").
    - **RELATIONSHIP:** Link the claim to the METHOD it describes.

    ### 5. LIMITATIONS (The "Gaps")
    - **INCLUDE:** Explicitly stated weaknesses, edge cases where the method fails, or hardware bottlenecks.
    - **EXCLUDE:** General research challenges not specific to the authors' findings.

    # CHAIN-OF-THOUGHT (Reasoning Steps)
    Before outputting JSON, perform these steps:
    1. **Inventory:** Identify every noun/phrase that fits a category.
    2. **The "Ownership" Test:** Does the text use "we propose," "our," or "this paper introduces"? If not, it is likely a BASELINE or PRIOR WORK.
    3. **The Relationship Map:** For every Dataset, Metric, or Claim, determine which specific METHOD it belongs to. If no method is named, link it to the Paper Title.

    # OUTPUT FORMAT (STRICT JSON)
    Return ONLY a JSON object. NO PROSE. DO NOT USE MARKDOWN LIKE ```json ```

    {{
      "reasoning_log": "A 2-sentence summary of your logic for this chunk.",
      "entities": [
        {{
          "type": "METHOD",
          "name": "Name",
          "status": "PROPOSED or BASELINE",
          "novelty_score": 1-5,
          "evidence": "Quote from text"
        }},
        {{
          "type": "DATASET",
          "name": "Name",
          "associated_method": "Name of Method it was used for",
          "evidence": "Quote from text"
        }},
        {{
          "type": "METRIC",
          "name": "Name",
          "associated_method": "Name of Method measured",
          "evidence": "Quote from text"
        }},
        {{
          "type": "CLAIM",
          "statement": "The claim",
          "associated_method": "Method name",
          "evidence": "Quote from text"
        }},
        {{
          "type": "LIMITATION",
          "description": "The limitation",
          "associated_method": "Method name",
          "evidence": "Quote from text"
        }}
      ]
    }}
    
    DO NOT USE MARKDOWN LIKE ```json ```
    """
  prompt = f"{SCHEMA}\n\nTEXT:\n{text}"
  
  
  res = client.models.generate_content(
    model=model_name,
    contents=prompt
  )
  
  try:
    return parse_llm_json(raw_output=res.text)
  except Exception as e:
    return{
      "methods": [],
      "datasets": [],
      "metrics": [],
      "limitations": [],
      "claims": []
    }
