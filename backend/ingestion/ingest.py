from ingestion.loader import load_pdf
from ingestion.chunker import chunk_text
from ingestion.embedder import upload_chunks
from retrieval.vector_retriever import retrieve_chunks as vector_search
from graph.extractor import extract_entities
from graph.store import add_knowledge

  
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


async def ingest(pdf_stream, pdf_name: str, user_id):
  try:
    text = load_pdf(pdf_stream)
    chunks = chunk_text(text, max_words=500)
    upload_chunks(chunks, paper_id=pdf_name,user_id=user_id)

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
        
        add_knowledge(paper_id=pdf_name.strip(), entities_json= ents,unique_methods=unique_methods,user_id=user_id)
        curr_budget+=1

  
  except Exception as e:
    return f"Error: {e}"
