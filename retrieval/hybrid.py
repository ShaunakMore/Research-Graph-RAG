from retrieval.vector_retriever import retrieve_chunks as vector_search
from graph.query import query_graph
from graph.intent import detect_intent

def hybrid_content(query,paper_list,user_id):
  
  intent = detect_intent(query,paper_list)
  
  graph = query_graph(intent,user_id=user_id)
  
  retrieved_vectors = f""
  if intent["paper_ids"]:
    for paper in intent["paper_ids"]: 
      vec = vector_search(query,paper=paper,user_id=user_id)
      retrieved_vectors += f"""
      PAPER: {paper}
      RETRIEVED CHUNKS:
      {vec}
      """
  else:
    vec = vector_search(query,paper=None,user_id=user_id)
  
  return retrieved_vectors,graph,intent