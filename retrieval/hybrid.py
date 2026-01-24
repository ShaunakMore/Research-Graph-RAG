from retrieval.vector_retriever import retrieve_chunks as vector_search
from graph.query import query_graph
from graph.intent import detect_intent

def hybrid_content(query):
  
  intent = detect_intent(query)
  
  graph = query_graph(intent)
  
  vec = vector_search(query)
  
  return vec,graph,intent