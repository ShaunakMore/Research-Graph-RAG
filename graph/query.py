from neo4j import GraphDatabase
from dotenv import load_dotenv
import os
load_dotenv()

driver = GraphDatabase.driver(
  os.getenv("NEO4J_URI"), #type:ignore
  auth=(os.getenv("NEO4J_USER"),os.getenv("NEO4J_PASSWORD")) #type:ignore
)

def prepare_result(results):
    graph_res = ""
    for i, rows in enumerate(results):
        for res in rows:
            paper = res.get("paper", "UNKNOWN")
            method = res.get("method", "")
            
            # This ensures we don't say "METHOD: " if we fell back to Paper-level data
            method_line = f"METHOD: {method}\n" if method else ""

            for key, value in res.items():
                if key in ["paper", "method"]: continue

                # If the CASE statement returned an empty list for both, show "None Found"
                if isinstance(value, list):
                    joined = ", ".join(value) if value else "None Found"
                else:
                    joined = str(value) if value else "None Found"

                graph_res += f"[GRAPH_{i+1}]\nPAPER: {paper}\n{method_line}{key.upper()}: {joined}\n\n"
    return graph_res


def query_graph(intent):
    print(f"\nRecieved intent: {intent}\n")

    e = intent["entities"]
    t = intent["type"]
    results = []
    if not e:
        return results
    for ent in e:
        # ----- STEP 1: Find entity nodes -----
        
        # print(f"\nChosen Entity: {entity}\n")
        # print(f"\nChosen question type: {t}\n")

        paper_query = """
        MATCH (n)
        WHERE toLower(n.name) CONTAINS toLower($e)
            OR toLower($e) CONTAINS toLower(n.name)

        OPTIONAL MATCH (p:Paper)-[]->(n)

        RETURN DISTINCT
        coalesce(p.name, n.name) as paper
        LIMIT 1
        """

        with driver.session() as s:
            paper_res = s.run(paper_query, e=ent).data()

        if not paper_res:
            continue

        paper = paper_res[0]["paper"]
        print(f"\nResolved Paper: {paper}\n")

        # ----- METHOD QUESTION -----
        if t == "method":

            q = """
            MATCH (p:Paper {name:$paper})
            OPTIONAL MATCH (p)-[:PROPOSES]->(m:Method)

            RETURN
            p.name as paper,
            collect(DISTINCT m.name) as methods
            """

        # ----- DATASET QUESTION -----
        elif t == "dataset":
            q = """
            MATCH (p:Paper {name:$paper})
            
            OPTIONAL MATCH (p)-[:PROPOSES]->(m:Method)
            WHERE toLower(m.name) CONTAINS toLower($e)
            
            OPTIONAL MATCH (m)-[:EVALUATED_ON]->(d:Dataset)
            
            OPTIONAL MATCH (p)-[:EVALUATED_ON]->(d2:Dataset)
            WHERE m IS NULL
            
            RETURN 
                p.name as paper, 
                coalesce(m.name, "") as method, 
                collect(DISTINCT d.name) + collect(DISTINCT d2.name) as datasets
            """
    # Use 'e=ent' in your s.run() call

        # ----- METRIC QUESTION -----
        elif t == "metric":
            q = """
            MATCH (p:Paper {name:$paper})
            OPTIONAL MATCH (p)-[:PROPOSES]->(m:Method)
            WHERE toLower(m.name) CONTAINS toLower($e)
            
            OPTIONAL MATCH (m)-[:MEASURED_BY]->(met:Metric)
            
            OPTIONAL MATCH (p)-[:MEASURED_BY]->(met2:Metric)
            WHERE m IS NULL
            
            RETURN 
                p.name as paper, 
                coalesce(m.name, "") as method, 
                collect(DISTINCT met.name) + collect(DISTINCT met2.name) as metrics
            """

        # ----- LIMITATION QUESTION -----
        elif t == "limitation":
            q = """
            MATCH (p:Paper {name:$paper})
            OPTIONAL MATCH (p)-[:PROPOSES]->(m:Method)
            WHERE toLower(m.name) CONTAINS toLower($e)
            
            OPTIONAL MATCH (m)-[:HAS_LIMITATION]->(l:Limitation)
            
            OPTIONAL MATCH (p)-[:HAS_LIMITATION]->(l2:Limitation)
            WHERE m IS NULL
            
            RETURN 
                p.name as paper, 
                coalesce(m.name, "") as method, 
                collect(DISTINCT l.text) + collect(DISTINCT l2.text) as limitations
            """
        # ----- CLAIM QUESTION -----
        elif t in ["claim", "claims"]:
            q = """
            MATCH (p:Paper {name:$paper})
            OPTIONAL MATCH (p)-[:PROPOSES]->(m:Method)
            WHERE toLower(m.name) CONTAINS toLower($e)
            
            OPTIONAL MATCH (m)-[:ACHIEVED]->(c:Claim)
            
            OPTIONAL MATCH (p)-[:ACHIEVED]->(c2:Claim)
            WHERE m IS NULL
            
            RETURN 
                p.name as paper, 
                coalesce(m.name, "") as method, 
                collect(DISTINCT c.text) + collect(DISTINCT c2.text) as claims
            """
        else:
            continue

        with driver.session() as s:
            results.append(s.run(q, paper=paper,e=ent).data()) 
    
    return prepare_result(results)