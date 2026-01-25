import google.genai as genai
import ollama
import os
from dotenv import load_dotenv
import json
import re

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY")) 
model_name = os.getenv("GOOGLE_MODEL")

# SCHEMA = """
# You are a STRICT academic information extractor.

# Your task is to extract ONLY explicitly stated, paper-owned information.
# Do NOT guess.

# If an item is not CLEARLY and EXPLICITLY stated in the text, DO NOT include it.

# ====================================
# CORE PRINCIPLE (MOST IMPORTANT)
# ====================================

# This paper is the ONLY source of truth.

# - Include information ONLY if the paper itself claims, proposes, uses, or reports it.
# - If the paper merely mentions something from prior work, DO NOT include it.
# - If ownership is ambiguous, EXCLUDE it.

# ====================================
# CATEGORY DEFINITIONS
# ====================================

# 1. METHODS / APPROACHES

# Include ONLY methods, models, algorithms, or techniques that are:
# - explicitly PROPOSED, INTRODUCED, or PRESENTED by THIS paper


# EXCLUDE:
# - baseline models
# - comparison systems
# - prior work methods
# - architectures cited from other papers
# - optimizers, training tricks, libraries, or frameworks
# - hyperparameters (learning rate, epochs, batch size)
# - implementation details
# - generic terms without a proper name
# - figure labels, equation symbols, tokens, or variable names

# Use the canonical method name only (1-4 words).

# ------------------------------------

# 2. DATASETS / DATA SOURCES

# Include ONLY real datasets, corpora, benchmarks, or data collections that:
# - are explicitly stated as being USED, TRAINED ON, or EVALUATED ON by THIS paper

# Examples:
# - SQuAD
# - ImageNet
# - Wikipedia
# - BooksCorpus
# - MIMIC

# EXCLUDE:
# - tasks or problem names
# - evaluation suites unless they are actual datasets
# - synthetic or hypothetical data
# - dataset splits unless they have a proper dataset name

# ------------------------------------

# 3. METRICS / EVALUATION MEASURES

# Include ONLY explicit evaluation metrics used to assess performance.

# Examples:
# - Accuracy
# - F1
# - BLEU
# - ROUGE
# - RMSE
# - AUC
# - Precision
# - Recall

# Rules:
# - Include the metric NAME only
# - Do NOT include numerical values
# - Do NOT include tables, scores, or results without a metric name

# ------------------------------------

# 4. LIMITATIONS

# Include ONLY limitations or weaknesses that are:
# - explicitly stated or clearly acknowledged by the paper

# Examples:
# - scalability issues
# - data requirements
# - architectural constraints
# - ethical or bias concerns
# - computational cost limitations

# Rules:
# - If the paper does NOT clearly state a limitation, RETURN an empty list []
# - Do NOT infer or assume limitations
# - Do NOT restate known drawbacks unless explicitly written

# ------------------------------------

# 5. CLAIMS

# Include ONLY explicit high-level claims made by THIS paper.

# Rules:
# - Claims must be factual statements made by the paper
# - Keep claims short and literal
# - Do NOT paraphrase or interpret
# - Do NOT add explanations

# ====================================
# FORMATTING RULES (STRICT)
# ====================================

# - Return VALID JSON ONLY
# - Use EXACTLY the following structure
# - Do NOT add extra keys
# - Do NOT include explanations
# - Do NOT use markdown
# - JSON must be directly parseable

# ====================================
# OUTPUT FORMAT
# ====================================

# {
#   "methods": [],
#   "datasets": [],
#   "metrics": [],
#   "limitations": [],
#   "claims": []
# }

# """


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
  
  # res = ollama.chat(
  #   model="mistral",
  #   messages=[{"role":"user","content":prompt}]
  # )
  
  # try:
  #   return json.loads(res["message"]["content"])
  # except:
  #   return{
  #     "methods": [],
  #     "datasets": [],
  #     "metrics": [],
  #     "limitations": [],
  #     "claims": []
  #   }
  
  res = client.models.generate_content(
    model="gemma-3-27b-it",
    contents=prompt
  )
  
  print(f"Gemini_response generate")
  try:
    return parse_llm_json(raw_output=res.text)
  except Exception as e:
    print(f"Extraction error {e}")
    return{
      "methods": [],
      "datasets": [],
      "metrics": [],
      "limitations": [],
      "claims": []
    }
