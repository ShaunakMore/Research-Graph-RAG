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
            MATCH (p:Paper {name: $paper})
            
            OPTIONAL MATCH (p)-[:PROPOSES]->(m:Method)
            WHERE toLower(m.name) = toLower($e)
            OPTIONAL MATCH (m)-[:EVALUATED_ON]->(d:Dataset)
            WITH p, m, collect(DISTINCT d.name) as method_datasets
            
            OPTIONAL MATCH (p)-[:EVALUATED_ON]->(pd:Dataset)
            WITH p, m, method_datasets, collect(DISTINCT pd.name) as paper_datasets
            
            RETURN 
                p.name as paper,
                coalesce(m.name, "") as method,
                CASE 
                    WHEN size(method_datasets) > 0 THEN method_datasets
                    ELSE paper_datasets
                END as datasets
            """
    # Use 'e=ent' in your s.run() call

        # ----- METRIC QUESTION -----
        elif t == "metric":
            q = """
            MATCH (p:Paper {name: $paper})
            
            // 1. Target specific method first
            OPTIONAL MATCH (p)-[:PROPOSES]->(m:Method)
            WHERE toLower(m.name) = toLower($e)
            OPTIONAL MATCH (m)-[:MEASURED_BY]->(met:Metric)
            WITH p, m, collect(DISTINCT met.name) as method_metrics
            
            // 2. Paper-level fallback
            OPTIONAL MATCH (p)-[:MEASURED_BY]->(p_met:Metric)
            WITH p, m, method_metrics, collect(DISTINCT p_met.name) as paper_metrics
            
            // 3. Return method results if they exist, otherwise paper results
            RETURN 
                p.name as paper,
                coalesce(m.name, "") as method,
                CASE 
                    WHEN size(method_metrics) > 0 THEN method_metrics
                    ELSE paper_metrics
                END as metrics
            """

        # ----- LIMITATION QUESTION -----
        elif t == "limitation":
            q = """
            MATCH (p:Paper {name: $paper})
            
            // 1. Target specific method first
            OPTIONAL MATCH (p)-[:PROPOSES]->(m:Method)
            WHERE toLower(m.name) = toLower($e)
            OPTIONAL MATCH (m)-[:HAS_LIMITATION]->(l:Limitation)
            WITH p, m, collect(DISTINCT l.text) as method_limitations
            
            // 2. Paper-level fallback
            OPTIONAL MATCH (p)-[:HAS_LIMITATION]->(p_l:Limitation)
            WITH p, m, method_limitations, collect(DISTINCT p_l.text) as paper_limitations
            
            RETURN 
                p.name as paper,
                coalesce(m.name, "") as method,
                CASE 
                    WHEN size(method_limitations) > 0 THEN method_limitations
                    ELSE paper_limitations
                END as limitations
            """
        # ----- CLAIM QUESTION -----
        elif t in ["claim", "claims"]:
            q = """
            MATCH (p:Paper {name: $paper})
            
            // 1. Target specific method first
            OPTIONAL MATCH (p)-[:PROPOSES]->(m:Method)
            WHERE toLower(m.name) = toLower($e)
            OPTIONAL MATCH (m)-[:ACHIEVED]->(c:Claim)
            WITH p, m, collect(DISTINCT c.text) as method_claims
            
            // 2. Paper-level fallback
            OPTIONAL MATCH (p)-[:ACHIEVED]->(p_c:Claim)
            WITH p, m, method_claims, collect(DISTINCT p_c.text) as paper_claims
            
            RETURN 
                p.name as paper,
                coalesce(m.name, "") as method,
                CASE 
                    WHEN size(method_claims) > 0 THEN method_claims
                    ELSE paper_claims
                END as claims
            """
        else:
            continue

        with driver.session() as s:
            results.append(s.run(q, paper=paper,e=ent).data()) 
    
    return prepare_result(results)