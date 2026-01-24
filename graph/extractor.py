import google.genai as genai
import ollama
import json,os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY")) 
model_name = os.getenv("GOOGLE_MODEL")

SCHEMA = """
You are a STRICT academic information extractor.

Your task is to extract ONLY explicitly stated, paper-owned information.
Do NOT guess.

If an item is not CLEARLY and EXPLICITLY stated in the text, DO NOT include it.

====================================
CORE PRINCIPLE (MOST IMPORTANT)
====================================

This paper is the ONLY source of truth.

- Include information ONLY if the paper itself claims, proposes, uses, or reports it.
- If the paper merely mentions something from prior work, DO NOT include it.
- If ownership is ambiguous, EXCLUDE it.

====================================
CATEGORY DEFINITIONS
====================================

1. METHODS / APPROACHES

Include ONLY methods, models, algorithms, or techniques that are:
- explicitly PROPOSED, INTRODUCED, or PRESENTED by THIS paper


EXCLUDE:
- baseline models
- comparison systems
- prior work methods
- architectures cited from other papers
- optimizers, training tricks, libraries, or frameworks
- hyperparameters (learning rate, epochs, batch size)
- implementation details
- generic terms without a proper name
- figure labels, equation symbols, tokens, or variable names

Use the canonical method name only (1-4 words).

------------------------------------

2. DATASETS / DATA SOURCES

Include ONLY real datasets, corpora, benchmarks, or data collections that:
- are explicitly stated as being USED, TRAINED ON, or EVALUATED ON by THIS paper

Examples:
- SQuAD
- ImageNet
- Wikipedia
- BooksCorpus
- MIMIC

EXCLUDE:
- tasks or problem names
- evaluation suites unless they are actual datasets
- synthetic or hypothetical data
- dataset splits unless they have a proper dataset name

------------------------------------

3. METRICS / EVALUATION MEASURES

Include ONLY explicit evaluation metrics used to assess performance.

Examples:
- Accuracy
- F1
- BLEU
- ROUGE
- RMSE
- AUC
- Precision
- Recall

Rules:
- Include the metric NAME only
- Do NOT include numerical values
- Do NOT include tables, scores, or results without a metric name

------------------------------------

4. LIMITATIONS

Include ONLY limitations or weaknesses that are:
- explicitly stated or clearly acknowledged by the paper

Examples:
- scalability issues
- data requirements
- architectural constraints
- ethical or bias concerns
- computational cost limitations

Rules:
- If the paper does NOT clearly state a limitation, RETURN an empty list []
- Do NOT infer or assume limitations
- Do NOT restate known drawbacks unless explicitly written

------------------------------------

5. CLAIMS

Include ONLY explicit high-level claims made by THIS paper.

Rules:
- Claims must be factual statements made by the paper
- Keep claims short and literal
- Do NOT paraphrase or interpret
- Do NOT add explanations

====================================
FORMATTING RULES (STRICT)
====================================

- Return VALID JSON ONLY
- Use EXACTLY the following structure
- Do NOT add extra keys
- Do NOT include explanations
- Do NOT use markdown
- JSON must be directly parseable

====================================
OUTPUT FORMAT
====================================

{
  "methods": [],
  "datasets": [],
  "metrics": [],
  "limitations": [],
  "claims": []
}

"""


def extract_entities(text):
  
  prompt = f"{SCHEMA}\n\nTEXT:\n{text}"
  
  res = ollama.chat(
    model="llama3.2",
    messages=[{"role":"user","content":prompt}]
  )
  
  try:
    return json.loads(res["message"]["content"])
  except:
    return{
      "methods": [],
      "datasets": [],
      "metrics": [],
      "limitations": [],
      "claims": []
    }
  
  # res = client.models.generate_content(
  #   model="gemma-3-27b-it",
  #   contents=prompt
  # )
  
  # try:
  #   return json.loads(res.text)
  # except Exception as e:
  #   print(f"Extraction error {e}")
  #   return{
  #     "methods": [],
  #     "datasets": [],
  #     "metrics": [],
  #     "limitations": [],
  #     "claims": []
  #   }
