from ingestion.loader import load_pdf
from ingestion.chunker import chunk_text
from ingestion.embedder import upload_chunks
from retrieval.vector_retriever import retrieve_chunks as vector_search
from graph.extractor import extract_entities
from graph.store import add_knowledge

async def ingest(pdf_path,pdf_name):
  try:
    text = load_pdf(pdf_path)
    chunks = chunk_text(text, max_words=300)
    upload_chunks(chunks, paper_id=pdf_name)
    chunks = vector_search(pdf_name,top_k=20)

    for c in chunks:
      ents  = extract_entities(c)
      print("ENTITIES:", ents)
      add_knowledge(pdf_name,ents)

    print("Graph populated successfully.")
    return f"Pdf uploaded to both graph and vector db"
  except Exception as e:
    return f"Error: {e}"
  