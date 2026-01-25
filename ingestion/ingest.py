from ingestion.loader import load_pdf
from ingestion.chunker import chunk_text
from ingestion.embedder import upload_chunks
from retrieval.vector_retriever import retrieve_chunks as vector_search
from graph.extractor import extract_entities
from graph.store import add_knowledge

# async def ingest(pdf_path,pdf_name):
#   try:
#     text = load_pdf(pdf_path)
#     chunks = chunk_text(text, max_words=300)
#     upload_chunks(chunks, paper_id=pdf_name)
#     chunks = vector_search(pdf_name,top_k=20)

#     for c in chunks:
#       ents  = extract_entities(c)
#       print("ENTITIES:", ents)
#       add_knowledge(pdf_name,ents)

#     print("Graph populated successfully.")
#     return f"Pdf uploaded to both graph and vector db"
#   except Exception as e:
#     return f"Error: {e}"
  
BLACKLIST_SECTIONS = {
    "related work",
    "background",
    "prior work",
    "literature review",
    "baselines",
    "implementation details",
    "appendix",
    "supplementary",
    "supplemental",
    "acknowledgements",
    "acknowledgments",
    "references"
}

GRAPH_BUDGET = 30

def is_chunk_useful(result):
    return result.get("entities")
    
def should_use_for_graph(section: str) -> bool:
    if not section:
        return False

    section = section.lower()

    # reject blacklisted sections
    for bad in BLACKLIST_SECTIONS:
        if bad in section:
            return False

    return True


async def ingest(pdf_path: str, pdf_name: str):
  try:
    text = load_pdf(pdf_path)
    chunks = chunk_text(text, max_words=500)
    upload_chunks(chunks, paper_id=pdf_name)

    curr_budget = 0
    unique_methods = set()
    for c in chunks:
        if(curr_budget >= GRAPH_BUDGET):
            break
        
        section = c.get("section", "")

        if not should_use_for_graph(section):
            continue

        ents = extract_entities(paper_name=pdf_name,section=section,text=c["text"])
        
        if(not is_chunk_useful(ents)):
            continue
        
        add_knowledge(pdf_name.strip(), ents,unique_methods)
        print(unique_methods)
        curr_budget+=1

    print(f"[INGEST] Graph populated and vector db updated successfully for {pdf_name}")
  
  except Exception as e:
    return f"Error: {e}"
